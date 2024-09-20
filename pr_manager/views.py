import logging

from django.conf import settings
from django.shortcuts import render
from django.core.cache import cache
from github import Github

g = Github(settings.GITHUB_PAT)
logger = logging.getLogger(__name__)


def get_prs():

    # Try fetching cached PRs first
    cached_pulls = cache.get('all_pull_requests')

    if cached_pulls:
        logger.info("Returning cached pull requests")
        return cached_pulls

    all_pulls = []
    for repo in g.get_user().get_repos():
        pulls = repo.get_pulls(state='open')
        logger.info(f"Found {pulls.totalCount} PRs in {repo.name}")
        for pr in pulls:
            all_pulls.append(pr)
    # Cache the result for 1 hour (3600 seconds)
    cache.set('all_pull_requests', all_pulls, timeout=3600)
    return all_pulls


def index(request):
    return render(request, "index.html", {
        "prs": get_prs(),
    })