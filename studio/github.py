import logging
import re

from django.conf import settings
from django.core.cache import cache
from github import Github

g = Github(settings.GITHUB_PAT)
logger = logging.getLogger(__name__)


# Regular expression to match owner and repo
pattern = r'https:\/\/github\.com\/([^\/]+)\/([^\/]+)\/commit\/[^\/]+'


def get_prs(repo_name):
    all_pulls = []
    repo = g.get_repo(repo_name)
    pulls = repo.get_pulls(state='open')
    logger.info(f"Found {pulls.totalCount} PRs in {repo.name}")
    for pr in pulls:
        all_pulls.append(pr)

    return all_pulls


def get_cached_user():
    """Caches Github user using hashed access token"""
    cache_key = f'github_user_{hash(settings.GITHUB_PAT)}'
    user = cache.get(cache_key)
    if user:
        logger.info("Returning cached user")
        return user
    user = g.get_user()
    cache.set(cache_key, user, timeout=3600)
    return user

def get_user_repos():
    user = get_cached_user()
    # Try fetching cached PRs first
    cached_repos = cache.get(f'user_repos_{user.login}')

    if cached_repos:
        logger.info("Returning cached user repos")
        return cached_repos

    search_query = f"author:{user.login}"
    commit_results = g.search_commits(query=search_query, sort="author-date", order="desc")

    # Store the last 5 unique repositories where you made commits
    recent_repos = set()
    for commit in commit_results:
        # Perform the regex search
        match = re.search(pattern, commit.html_url)
        if match:
            owner = match.group(1)
            repo = match.group(2)
            repo_name = f"{owner}/{repo}"
        else:
            raise ValueError(f"Failed to match regex for {commit.html_url}")
        if repo_name not in [repo.full_name for repo in recent_repos]:
            logger.info(f"Found repo {repo_name}")
            recent_repos.add(g.get_repo(repo_name))
        if len(recent_repos) == 5:
            break
    logger.info(f"Found {len(recent_repos)} repos for user {user.login}")
    cache.set(f'user_repos_{user.login}', recent_repos, timeout=3600)
    return recent_repos


def list_repos_by_owner():
    cache_key = f'user_repos_{hash(settings.GITHUB_PAT)}'
    cached_repos = cache.get(cache_key)
    if cached_repos:
        logger.info("Returning cached user repos")
        return cached_repos
    repos = get_user_repos()
    repos_by_owner = {}
    for repository in repos:
        owner_name = repository.owner.login
        if owner_name not in repos_by_owner:
            repos_by_owner[owner_name] = []
        repos_by_owner[owner_name].append(repository)
    cache.set(cache_key, repos_by_owner, timeout=3600)
    return repos_by_owner
