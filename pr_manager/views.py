import json
import logging

import arcane
from arcane.engine import ArcaneEngine
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from github import Github

from repositories.models import BookmarkedRepo
from repositories.views import render_with_repositories
from studio.github import get_prs, get_user_repos, list_repos_by_owner
from studio.prompts import PR_DESCRIPTION

g = Github(settings.GITHUB_PAT)
logger = logging.getLogger(__name__)


@login_required
def view_pull_requests(request, owner=None, repo=None):
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
        prs = get_prs(f"{owner}/{repo}")
    return render_with_repositories(request, "index.html", {
        "prs": prs,
        "active_tab": "pull-request-manager",
    }, owner, repo)


@login_required
@require_POST
def generate_description(request, owner, repo):
    pr_number = request.POST.get('pr_number')
    engine = ArcaneEngine()
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
            "repos": list_repos_by_owner(),
            "error": msg
        })

    return redirect(reverse('view_task', args=(owner, repo, task.id,)))


