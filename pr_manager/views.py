import json
import logging

import arcane
import requests
from arcane.engine import ArcaneEngine
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST
from github import Github, GithubException

from repositories.models import BookmarkedRepo
from repositories.views import render_with_repositories
from studio.decorators import needs_api_key
from studio.github import get_github_token
from studio.prompts import PR_DESCRIPTION

logger = logging.getLogger(__name__)


def home(request):
    if not request.user.is_authenticated:
        return render(request, "pr_manager_preview.html", {
            "active_tab": "pull-request-manager",
        })
    return redirect("view_pull_requests", owner=None, repo=None)


@login_required
def view_pull_requests(request, owner=None, repo=None, pr_number=None):
    if not owner or owner == 'None':
        first_bookmark = BookmarkedRepo.objects.first()
        if first_bookmark:
            owner = first_bookmark.owner
            repo = first_bookmark.repo_name
        else:
            return redirect('repositories:repo_overview')
    if not owner or not repo:
        prs = []
    else:
        try:
            g = Github(get_github_token(request))
            github_repo = g.get_repo(f"{owner}/{repo}")
        except GithubException as e:
            return render(request, "error.html", {"error": str(e)})
        prs = github_repo.get_pulls(state='open')
        if not pr_number:
            selected_pr = prs[0]
        else:
            for pr in prs:
                if pr.number == pr_number:
                    selected_pr = pr
                    break
    diff_url = selected_pr.diff_url  # This gives us the URL to fetch the diff
    headers = {'Accept': 'application/vnd.github.v3.diff'}
    diff_data = requests.get(diff_url, headers=headers).text

    return render_with_repositories(request, "index.html", {
        "prs": prs,
        "selected_pr": selected_pr,
        "diff_data": diff_data,
        "active_tab": "pull-request-manager",
    }, owner, repo)


@login_required
@require_POST
@needs_api_key
def generate_description(request, api_key):
    pr_number = request.POST.get('pr_number')
    owner = request.POST.get('owner')
    repo = request.POST.get('repo')
    engine = ArcaneEngine(api_key)
    prompt = PR_DESCRIPTION.format(pr_number=pr_number)
    try:
        task = engine.create_task(f"{owner}/{repo}", prompt)
    except arcane.exceptions.ApiException as e:
        logger.error(f"Failed to create task: {e}")
        msg = str(e)
        parsed_json = json.loads(e.body)
        if parsed_json.get('details'):
            msg = parsed_json.get('details')
        return render(request, "error.html", {
            "error": msg
        })

    return redirect(reverse('view_task', args=(owner, repo, task.id,)))


