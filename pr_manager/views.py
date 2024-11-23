import hashlib
import json
import logging

import arcane
import requests
from arcane.engine import ArcaneEngine
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from github import Github
from github.GithubException import GithubException
from pydantic_core import from_json

from repositories.models import BookmarkedRepo
from repositories.views import render_with_repositories
from studio.decorators import needs_api_key
from studio.github import get_github_token
from .models import PullRequestDescription, PullRequestReview, ReviewFinding, PullRequestChangeRequest
from .prompts import emoji_prompt, structure_prompt, style_prompt, PR_DESCRIPTION, CODE_REVIEW, CodeReview, Category, \
    APPLY_RECOMMENDATION

logger = logging.getLogger(__name__)

category_colors = {
    Category.SECURITY: "is-danger",
    Category.PERFORMANCE: "is-warning",
    Category.USABILITY: "is-info",
    Category.FUNCTIONALITY: "is-success",
    Category.MAINTAINABILITY: "is-primary",
    Category.READABILITY: "is-link",
    Category.STYLE: "is-light",
    Category.OTHER: "is-dark"
}

def home(request):
    if not request.user.is_authenticated:
        return render(request, "pr_manager_preview.html", {
            "active_app": "pull-request-manager",
        })
    return redirect("view_pull_request_default", owner=None, repo=None)


def get_selected_pull_request(prs, pr_number):
    """Determine the selected pull request based on the provided PR number."""
    selected_pr = prs[0] if prs.totalCount > 0 else None
    for pr in prs:
        if pr.number == pr_number:
            selected_pr = pr
            break
    return selected_pr


def load_diff_data(github_token, owner, repo, pr_number):
    """Load the diff data for the selected pull request."""
    url = f"https://{github_token}:x-oauth-basic@api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {
        "Accept": "application/vnd.github.diff"
    }
    response = requests.get(url, headers=headers)
    if not response.ok:
        return None, f"Failed to load diff data: {response.text}"
    return response.text, None


def get_task_description(owner, repo, user, pr_number, api_key):
    """Retrieve the task description for the pull request if it exists."""
    description = PullRequestDescription.objects.filter(repo__owner=owner,
                                                        repo__repo_name=repo,
                                                        user=user,
                                                        pr_number=pr_number).first()
    task = None
    if description:
        task = ArcaneEngine(api_key).get_task(description.task_id)
    return task


def get_review_task(owner, repo, user, pr_number, api_key, selected_pr):
    """Retrieve and process the review task for the pull request if it exists."""
    review = PullRequestReview.objects.filter(repo__owner=owner,
                                              repo__repo_name=repo,
                                              pr_number=pr_number,
                                              user=user).first()
    review_task = None
    if review and not review.summary:
        if not review.task_id:
            review.delete()
            return None, redirect(reverse('view_pull_request', args=(owner, repo, pr_number,)))
        review_task = ArcaneEngine(api_key).get_task(review.task_id)
        if review_task.status == "completed":
            try:
                description = CodeReview.model_validate(from_json(review_task.result))
                logger.info(f"Successfully generated PR Review for {review_task.github_project} PR #{selected_pr.number}")
                review.delete()
                data = description.dict(exclude_unset=True)
                review = PullRequestReview.objects.create(
                    user=user,
                    repo=BookmarkedRepo.objects.get(owner=owner, repo_name=repo, user=user),
                    task_id=review_task.id,
                    pr_number=selected_pr.number,
                    summary=data.pop("summary"),
                )
                for finding in data.pop("findings"):
                    review.findings.create(**finding)
            except ValueError as e:
                logger.error("Failed to parse task result", exc_info=e)
                review.summary = f"Failed to parse task result: {str(e)}"
                review.save()
        elif review_task.status == "failed":
            review.summary = review_task.result
            review.save()
    return review_task, review


@login_required
@needs_api_key
def view_pull_request(request, owner: str = None, repo: str = None, pr_number: int = 0, pr_tab: str = "describe", api_key: str = None):
    """
    Main function to view a pull request, orchestrating helper functions.

    :param request: The HTTP request object.
    :param owner: The owner of the repository.
    :param repo: The name of the repository.
    :param pr_number: The pull request number.
    :param pr_tab: The tab to display in the pull request view.
    :param api_key: The API key for authentication.
    :return: HTTP response rendering the pull request view.
    """
    owner, repo = get_owner_and_repo(request, owner, repo)
    if not owner or not repo:
        return redirect('repositories:repo_overview')

    github_token = get_github_token(request)
    prs, error = fetch_pull_requests(github_token, owner, repo)
    if error:
        return handle_github_error(error, owner, repo)

    if prs.totalCount == 0:
        return render_with_repositories(request, "view_pull_request.html", {
            "prs": None,
            "selected_pr": 0,
            "diff_data": "",
            "active_app": "pull-request-manager",
        }, owner, repo)

    selected_pr = get_selected_pull_request(prs, pr_number)
    diff_data, error = load_diff_data(github_token, owner, repo, selected_pr.number)
    if error:
        return render(request, "error.html", {"error": error})

    task = get_task_description(owner, repo, request.user, selected_pr.number, api_key)
    review_task, review = get_review_task(owner, repo, request.user, selected_pr.number, api_key, selected_pr)
    commits = process_commits(selected_pr.get_commits())

    change_requests, change_request_task = process_change_requests(owner, repo, request.user, selected_pr.number, api_key)

    return render_with_repositories(request, "view_pull_request.html", {
        "review_task": review_task,
        "review": review,
        "prs": prs,
        "selected_pr": selected_pr,
        "diff_data": diff_data,
        "task": task,
        "active_app": "pull-request-manager",
        "pr_tab": pr_tab,
        "category_colors": category_colors,
        "commits": commits,
        "change_request_task": change_request_task,
        "change_requests": change_requests,
    }, owner, repo)

def get_owner_and_repo(request, owner: str, repo: str) -> tuple:
    """
    Retrieve the owner and repository name, defaulting to the first bookmarked repository if not provided.

    :param request: The HTTP request object.
    :param owner: The owner of the repository.
    :param repo: The name of the repository.
    :return: A tuple containing the owner and repository name.
    """
    if not owner or owner == 'None':
        first_bookmark = BookmarkedRepo.objects.filter(user=request.user).first()
        if first_bookmark:
            return first_bookmark.owner, first_bookmark.repo_name
    return owner, repo

def fetch_pull_requests(github_token: str, owner: str, repo: str):
    """
    Fetch open pull requests from the GitHub repository.

    :param github_token: The GitHub token for authentication.
    :param owner: The owner of the repository.
    :param repo: The name of the repository.
    :return: A tuple containing the pull requests and any error encountered.
    """
    try:
        g = Github(github_token)
        github_repo = g.get_repo(f"{owner}/{repo}")
        return github_repo.get_pulls(state='open'), None
    except GithubException as e:
        return None, e

def handle_github_error(error: GithubException, owner: str, repo: str):
    """
    Handle GitHub exceptions by redirecting or rendering an error page.

    :param error: The GitHub exception encountered.
    :param owner: The owner of the repository.
    :param repo: The name of the repository.
    :return: HTTP response for the error encountered.
    """
    if error.status == 401:
        return redirect(reverse('user_logout'))
    if error.status == 404:
        return redirect('repositories:install_repo', owner_name=owner, repo_name=repo)
    return render(request, "error.html", {"error": str(error)})

def process_commits(commits) -> list:
    """
    Process and enrich commit data with author information.

    :param commits: The list of commits to process.
    :return: A list of processed commits with author information.
    """
    processed_commits = []
    for commit in commits:
        if commit.author:
            commit.login = commit.author.login
            commit.avatar_url = commit.author.avatar_url
        else:
            commit.login, commit.avatar_url = get_commit_author_info(commit)
        processed_commits.append(commit)
    return processed_commits

def get_commit_author_info(commit) -> tuple:
    """
    Retrieve author information for a commit when the author is not directly available.

    :param commit: The commit object to retrieve author information for.
    :return: A tuple containing the username and avatar URL.
    """
    email = commit.commit.author.email
    username = commit.commit.author.name
    if email == "bot@arcane.engineer":
        avatar_url = "https://avatars.githubusercontent.com/in/845970?s=60&v=4"
    else:
        avatar_url = (
            f"https://www.gravatar.com/avatar/{hashlib.md5(email.encode()).hexdigest()}?d=identicon"
            if email else "https://github.com/identicons/default.png"
        )
    return username, avatar_url

def process_change_requests(owner: str, repo: str, user, pr_number: int, api_key: str) -> tuple:
    """
    Process change requests for a pull request, marking them as completed if necessary.

    :param owner: The owner of the repository.
    :param repo: The name of the repository.
    :param user: The user associated with the change requests.
    :param pr_number: The pull request number.
    :param api_key: The API key for authentication.
    :return: A tuple containing the change requests and the change request task.
    """
    change_requests = PullRequestChangeRequest.objects.filter(repo__owner=owner,
                                                              repo__repo_name=repo,
                                                              user=user,
                                                              pr_number=pr_number)
    change_request_task = None
    for change_request in [cr for cr in change_requests if not cr.completed]:
        if not change_request_task:
            change_request_task = ArcaneEngine(api_key).get_task(change_request.task_id)
            if change_request_task.status in ["completed", "failed"]:
                change_request.completed = True
                change_request.save()
    return change_requests, change_request_task
