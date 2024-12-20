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
def view_pull_request(request, owner=None, repo=None, pr_number=0, pr_tab="describe", api_key=None):
    """Main function to view a pull request, orchestrating helper functions."""
    if not owner or owner == 'None':
        first_bookmark = BookmarkedRepo.objects.filter(user=request.user).first()
        if first_bookmark:
            owner = first_bookmark.owner
            repo = first_bookmark.repo_name
            return redirect('view_pull_request_default_tab', owner=owner, repo=repo, pr_number=pr_number)
        else:
            return redirect('repositories:repo_overview')
    github_token = get_github_token(request)

    try:
        g = Github(github_token)
        github_repo = g.get_repo(f"{owner}/{repo}")
        prs = github_repo.get_pulls(state='open')
    except GithubException as e:
        if e.status == 401:
            return redirect(reverse('user_logout'))
        if e.status == 404:
            return redirect('repositories:install_repo', owner_name=owner, repo_name=repo)
        else:
            return render(request, "error.html", {
                "error": str(e),
            })

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

    # Get the commits for the selected PR
    commits = list(selected_pr.get_commits())
    for commit in commits:
        if commit.author:
            commit.login = commit.author.login
            commit.avatar_url = commit.author.avatar_url
        else:
            email = commit.commit.author.email
            username = commit.commit.author.name
            if email == "bot@arcane.engineer":
                avatar_url = "https://avatars.githubusercontent.com/in/845970?s=60&v=4"
            else:
                avatar_url = (
                    f"https://www.gravatar.com/avatar/{hashlib.md5(email.encode()).hexdigest()}?d=identicon"
                    if email
                    else "https://github.com/identicons/default.png"
                )
            commit.login = username
            commit.avatar_url = avatar_url

    # Find all non-completed change requests for the PR
    change_requests = PullRequestChangeRequest.objects.filter(repo__owner=owner,
                                                              repo__repo_name=repo,
                                                              user=request.user,
                                                              pr_number=selected_pr.number)
    change_request_task = None
    for change_request in [cr for cr in change_requests if not cr.completed]:
        if not change_request_task:
            change_request_task = ArcaneEngine(api_key).get_task(change_request.task_id)
            if change_request_task.status in ["completed", "failed"]:
                change_request.completed = True
                change_request.save()

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


@login_required
@require_POST
@needs_api_key
def generate_description(request, api_key):
    pr_number = request.POST.get('pr_number')
    owner = request.POST.get('owner')
    repo = request.POST.get('repo')
    emojis = request.POST.get('emojis')
    content_size = request.POST.get('content_size')
    structure = request.POST.get('structure')
    additional_instructions = request.POST.get('additional_instructions', '')

    engine = ArcaneEngine(api_key)
    prompt = PR_DESCRIPTION.format(
        pr_number=pr_number,
        structure=structure_prompt(structure),
        additional_instructions=additional_instructions,
        emojis=emoji_prompt(emojis),
        style=style_prompt(content_size)
    )

    try:
        task = engine.create_task(f"{owner}/{repo}", prompt)
        bookmark = BookmarkedRepo.objects.get(owner=owner, repo_name=repo)
        # Create a new PullRequestDescription instance

        PullRequestDescription.objects.filter(user=request.user, repo=bookmark).delete()
        PullRequestDescription.objects.create(
            user=request.user,
            repo=bookmark,
            pr_number=pr_number,
            task_id=task.id
        )
    except arcane.exceptions.ApiException as e:
        logger.error(f"Failed to create task: {e}")
        msg = str(e)
        parsed_json = json.loads(e.body)
        if parsed_json.get('details'):
            msg = parsed_json.get('details')
        return render(request, "error.html", {
            "error": msg
        })

    return redirect(reverse('view_pull_request', args=(owner, repo, pr_number, "describe")))


@login_required
@needs_api_key
def generate_review(request, api_key):
    repo = request.POST.get('repo')
    owner = request.POST.get('owner')
    pr_number = request.POST.get('pr_number')
    try:
        bookmark = BookmarkedRepo.objects.get(owner=owner, repo_name=repo, user=request.user)
    except BookmarkedRepo.DoesNotExist:
        return render(request, "error.html", {"error": "Repository not found"})

    engine = ArcaneEngine(api_key)
    review, _ = PullRequestReview.objects.get_or_create(user=request.user, repo=bookmark, pr_number=pr_number)
    task = engine.create_task(f"{owner}/{repo}", CODE_REVIEW.format(pr_number=pr_number),
                              output_format="json",
                              output_structure=json.dumps(CodeReview.model_json_schema()))
    review.task_id = task.id
    review.summary = None
    review.save()
    return redirect(reverse('view_pull_request', args=(owner, repo, pr_number, "review")))


@login_required
def reset_pr_review(request):
    repo = request.POST.get('repo')
    owner = request.POST.get('owner')
    pr_number = request.POST.get('pr_number')
    try:
        bookmark = BookmarkedRepo.objects.get(owner=owner, repo_name=repo, user=request.user)
    except BookmarkedRepo.DoesNotExist:
        return render(request, "error.html", {"error": "Repository not found"})

    review = PullRequestReview.objects.get(user=request.user, repo=bookmark, pr_number=pr_number)
    review.delete()
    return redirect(reverse('view_pull_request', args=(owner, repo, pr_number, "review")))


@login_required
@needs_api_key
def apply_recommendation(request, api_key):
    finding_id = request.POST.get('finding_id')
    finding = ReviewFinding.objects.get(id=finding_id)
    repo = finding.review.repo
    if not finding.review.user == request.user:
        return render(request, "error.html", {"error": "You are not authorized to apply this recommendation"})
    prompt = APPLY_RECOMMENDATION.format(
        file=finding.file,
        issue=finding.issue,
        recommendation=finding.recommendation
    )
    engine = ArcaneEngine(api_key)
    task = engine.create_task(repo.full_name, prompt, pr_number=finding.review.pr_number)
    finding.task_id = task.id
    finding.save()
    PullRequestChangeRequest.objects.create(
        user=request.user,
        repo=repo,
        pr_number=finding.review.pr_number,
        prompt=prompt,
        task_id=task.id
    )

    return redirect(reverse('view_pull_request', args=(repo.owner, repo.repo_name, finding.review.pr_number, "changes")))


@login_required
@needs_api_key
def dismiss_recommendation(request, api_key):
    finding_id = request.POST.get('finding_id')
    finding = ReviewFinding.objects.get(id=finding_id)
    repo = finding.review.repo
    # Check if the user has permission to dismiss the finding
    if not (finding.review.user == request.user or request.user.is_staff):
        return render(request, "error.html", {"error": "You are not authorized to dismiss this recommendation"})
    finding.dismissed = True
    finding.save()

    return redirect(reverse('view_pull_request', args=(repo.owner, repo.repo_name, finding.review.pr_number, "review")))


@login_required
@needs_api_key
def apply_change_request(request, api_key):
    change_request = request.POST.get('change_request')
    repo_owner = request.POST.get('repo_owner')
    repo_name = request.POST.get('repo_name')
    pr_number = request.POST.get('pr_number')
    try:
        repo = BookmarkedRepo.objects.get(owner=repo_owner, repo_name=repo_name, user=request.user)
        engine = ArcaneEngine(api_key)
        task = engine.create_task(f"{repo_owner}/{repo_name}", change_request, pr_number=pr_number)
        PullRequestChangeRequest.objects.create(
            user=request.user,
            repo=repo,
            pr_number=pr_number,
            prompt=change_request,
            task_id=task.id
        )
    except BookmarkedRepo.DoesNotExist:
        logger.error("Repository not found")
        return render(request, "error.html", {"error": "Repository not found"})
    except arcane.exceptions.ApiException as e:
        logger.error(f"Failed to create task: {e}")
        return render(request, "error.html", {"error": f"Failed to create task: {str(e)}"})
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return render(request, "error.html", {"error": "An unexpected error occurred. Please try again later."})

    return redirect(reverse('view_pull_request', args=(repo_owner, repo_name, pr_number, "changes")))


@login_required
@require_POST
def comment_on_pr_review(request):
    """Create a comment on a PR review in a particular line for a particular file"""
    line = int(request.POST.get('line'))
    file = request.POST.get('file')
    comment = request.POST.get('comment')
    try:
        g = Github(get_github_token(request))
        repo = g.get_repo(request.POST.get('repo'))
        pr = repo.get_pull(int(request.POST.get('pr_number')))
        commit = pr.get_commits().reversed[0]
        comment = pr.create_review_comment(body=comment, commit=commit, path=file, start_line=line)
    except GithubException as e:
        message = e.message
        if not message:
            message = str(e.data)
        return render(request, "error.html", {"error": f"Failed to create comment: {message}"})
    # Redirect to the comment URL
    return redirect(comment.html_url)

