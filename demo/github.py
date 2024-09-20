import logging

from django.conf import settings
from django.core.cache import cache
from github import Github

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


def list_repos_by_owner():
    repos = get_user_repos()
    repos_by_owner = {}
    for repository in repos:
        owner_name = repository.owner.login
        if owner_name not in repos_by_owner:
            repos_by_owner[owner_name] = []
        repos_by_owner[owner_name].append(repository)
    return repos_by_owner