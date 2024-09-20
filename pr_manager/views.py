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
        all_pulls.append({
            'repo': repo.name,
            'title': pr.title,
            'html_url': pr.html_url,
            'number': pr.number
        })
    # Cache the result for 1 hour (3600 seconds)
    cache.set(f'pull_requests_{repo_name}', all_pulls, timeout=3600)
    return all_pulls


def repo_list(request):
    user = g.get_user()
    repos = user.get_repos()
    repo_list = [repo.full_name for repo in repos]
    return render(request, "repo_list.html", {
        "repos": repo_list,
    })


def index(request, owner, repo):
    repo_name = f"{owner}/{repo}"
    prs = get_prs(repo_name)
    repos = {repo_name: prs}
    return render(request, "index.html", {
        "repos": repos,
        "pr_count": len(prs),
        "repo_count": 1
    })


@require_POST
def generate_description(request):
    repo = request.POST.get('repo')
    pr_number = request.POST.get('pr_number')
    # Here you would add the logic to generate the PR description
    # For now, we'll just log the repo and PR number
    logger.info(f"Generating description for PR {pr_number} in repo {repo}")
    return JsonResponse({'status': 'success'})
