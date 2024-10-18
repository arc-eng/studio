import json
import logging

import arcane
import requests
from arcane.engine import ArcaneEngine
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from github import Github, GithubException
from pydantic_core import from_json

from repositories.models import BookmarkedRepo
from repositories.views import render_with_repositories
from studio.decorators import needs_api_key
from studio.github import get_github_token
from .models import PullRequestDescription, PullRequestReview
from .prompts import emoji_prompt, structure_prompt, style_prompt, PR_DESCRIPTION, CODE_REVIEW, CodeReview, Category

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
            "active_tab": "pull-request-manager",
        })
    return redirect("view_pull_request_default", owner=None, repo=None)


@login_required
@needs_api_key
def view_pull_request(request, owner=None, repo=None, pr_number=0, pr_tab="describe", api_key=None):
    if not owner or owner == 'None':
        first_bookmark = BookmarkedRepo.objects.first()
        if first_bookmark:
            owner = first_bookmark.owner
            repo = first_bookmark.repo_name
            return redirect('view_pull_request_default_tab', owner=owner, repo=repo, pr_number=pr_number)
        else:
            return redirect('repositories:repo_overview')
    github_token = get_github_token(request)
    selected_pr = None
    if not owner or not repo:
        prs = []
    else:
        try:
            g = Github(github_token)
            github_repo = g.get_repo(f"{owner}/{repo}")
        except GithubException as e:
            if e.status == 401:
                # Log user out
                return redirect("user_logout")
            return render(request, "error.html", {"error": str(e)})
        prs = github_repo.get_pulls(state='open')

        if prs.totalCount == 0:
            return render_with_repositories(request, "view_pull_request.html", {
                "prs": None,
                "selected_pr": 0,
                "diff_data": "",
                "active_tab": "pull-request-manager",
            }, owner, repo)
        selected_pr = prs[0]
        for pr in prs:
            if pr.number == pr_number:
                selected_pr = pr
                break

    # Load the diff data for the selected PR
    url = f"https://{github_token}:x-oauth-basic@api.github.com/repos/{owner}/{repo}/pulls/{selected_pr.number}"
    headers = {
        "Accept": "application/vnd.github.diff"
    }
    response = requests.get(url, headers=headers)
    if not response.ok:
        return render(request, "error.html", {
            "error": f"Failed to load diff data: {response.text}"
        })
    diff_data = response.text

    # Check if there is a description for this PR
    description = PullRequestDescription.objects.filter(repo__owner=owner,
                                                        repo__repo_name=repo,
                                                        user=request.user,
                                                        pr_number=selected_pr.number).first()
    task = None
    if description:
        task = ArcaneEngine(api_key).get_task(description.task_id)


    # Check if there is a review for this PR
    review = PullRequestReview.objects.filter(repo__owner=owner,
                                              repo__repo_name=repo,
                                              pr_number=selected_pr.number,
                                              user=request.user).first()
    review_task = None
    if review and not review.summary:
        if not review.task_id:
            review.delete()
            return redirect(reverse('view_pull_request', args=(owner, repo, pr_number,)))
        review_task = ArcaneEngine(api_key).get_task(review.task_id)
        if review_task.status == "completed":
            try:
                description = CodeReview.model_validate(from_json(review_task.result))
                logger.info(f"Successfully generated PR Review for {review_task.github_project} PR #{selected_pr.number}")
                review.delete()
                data = description.dict(exclude_unset=True)
                review = PullRequestReview.objects.create(
                    user=request.user,
                    repo=BookmarkedRepo.objects.get(owner=owner, repo_name=repo, user=request.user),
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


    return render_with_repositories(request, "view_pull_request.html", {
        "review_task": review_task,
        "review": review,
        "prs": prs,
        "selected_pr": selected_pr,
        "diff_data": diff_data,
        "task": task,
        "active_tab": "pull-request-manager",
        "pr_tab": pr_tab,
        "category_colors": category_colors,
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

