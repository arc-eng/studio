import logging

from django.conf import settings
from django.shortcuts import render, redirect
from django.core.cache import cache
from github import Github
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.http import JsonResponse


g = Github(settings.GITHUB_PAT)
logger = logging.getLogger(__name__)


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
    user = g.get_user()
    return user.get_repos()


def index(request, owner=None, repo=None):
    repos = get_user_repos()
    if not owner or not repo:
        prs = []
    else:
        prs = get_prs(f"{owner}/{repo}")
    return render(request, "index.html", {
        "repos": repos,
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
    # Here you would add the logic to generate the PR description
    # For now, we'll just log the repo and PR number
    logger.info(f"Generating description for PR {pr_number} in repo {repo}")
    return redirect(reverse('show_repo', args=[owner, repo]))
