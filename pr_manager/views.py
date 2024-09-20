import logging
import os

import markdown
from arcane.engine import ArcaneEngine
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from github import Github

from demo.prompts import PR_DESCRIPTION


g = Github(settings.GITHUB_PAT)
logger = logging.getLogger(__name__)

# TODO Make this available as parameter on ArcaneEngine
os.environ.setdefault('PR_PILOT_API_KEY', settings.ARCANE_API_KEY)


def get_prs(repo_name):

    # Try fetching cached PRs first
    cached_pulls = cache.get(f'pull_requests_{repo_name}')

    if cached_pulls:
        logger.info("Returning cached pull requests")
        return cached_pulls

    all_pulls = []
    repo = g.get_repo(repo_name)
    pulls = repo.get_pulls(state='open')
    logger.info(f"Found {pulls.totalCount} PRs in {repo.name}")
    for pr in pulls:
        all_pulls.append(pr)

    # Cache the result for 1 hour (3600 seconds)
    cache.set(f'pull_requests_{repo_name}', all_pulls, timeout=3600)
    return all_pulls


def get_user_repos():

    # Try fetching cached PRs first
    cached_repos = cache.get('user_repos')

    if cached_repos:
        logger.info("Returning cached user repos")
        return cached_repos
    user = g.get_user()
    repos = user.get_repos()
    logger.info(f"Found {repos.totalCount} repos for user {user.login}")
    cache.set('user_repos', repos, timeout=3600)
    return repos


def show_repos(request, owner=None, repo=None):
    repos = get_user_repos()
    repos_by_owner = {}
    for repository in repos:
        owner_name = repository.owner.login
        if owner_name not in repos_by_owner:
            repos_by_owner[owner_name] = []
        repos_by_owner[owner_name].append(repository)
    if not owner or not repo:
        prs = []
    else:
        prs = get_prs(f"{owner}/{repo}")
    return render(request, "index.html", {
        "repos": repos_by_owner,
        "prs": prs,
        "pr_count": len(prs),
        "repo_count": repos.totalCount,
        "repo_owner": owner,
        "repo_name": repo,
        "selected_repo": f"{owner}/{repo}"
    })


@require_POST

def generate_description(request, owner, repo):
    pr_number = request.POST.get('pr_number')
    engine = ArcaneEngine()
    prompt = PR_DESCRIPTION.format(pr_number=pr_number)
    task = engine.create_task(f"{owner}/{repo}", prompt)

    return redirect(reverse('view_task', args=(task.id,)))


def view_task(request, task_id):
    task = ArcaneEngine().get_task(task_id)
    task.result = markdown.markdown(task.result)
    task.user_request = markdown.markdown(task.user_request)
    return render(request, "view_task.html", {
        "task": task
    })
