from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import render, redirect
from github import Github, UnknownObjectException

from studio.github import get_github_token
from .models import BookmarkedRepo

PAGE_SIZE = 10


def render_paginated_repo_picker(request, repos, repo_count, search_query=None):
    page_count = int(repo_count / PAGE_SIZE) + 1
    page = int(request.GET.get('page', 1))

    if page_count <= 8:
        page_buttons = range(2, page_count - 1)
    else:
        if page == 1:
            page_buttons = [2, 3, 4]
        elif page == page_count:
            page_buttons = [page - 3, page - 2, page - 1]
        elif page == 2:
            page_buttons = [2, 3, 4]
        elif page == page_count - 1:
            page_buttons = [page - 2, page - 1, page]
        else:
            page_buttons = [page - 1, page, page + 1]

    return render(request, 'repositories/repo_picker.html', {
        'search_query': search_query,
        'repositories': repos.get_page(page - 1),
        'total_page_count': page_count,
        'current_page': page,
        'page_buttons': page_buttons,
        'prev_page': page - 1,
        'next_page': page + 1,
    })


@login_required
# @cache_page(60 * 15, cache="special_cache")
def show_repo_picker(request):
    g = Github(get_github_token(request), per_page=PAGE_SIZE)
    github_user = g.get_user()

    # Find user repos in Django cache
    repos = cache.get(f"{github_user.login}_repos")
    repos_count = cache.get(f"{github_user.login}_repos_count")

    if not repos:
        repos = github_user.get_repos(sort='pushed', direction='desc')
        repos_count = repos.totalCount
        cache.set(f"{github_user.login}_repos", repos, 60 * 5)
        cache.set(f"{github_user.login}_repos_count", repos_count, 60 * 5)

    return render_paginated_repo_picker(request, repos, repos_count)


@login_required
def repo_overview(request):
    return render_with_repositories(request, 'repositories/overview.html', {
        'active_tab': 'bookmarks',
    })


@login_required
def bookmark_repo(request, org_name, repo_name):
    BookmarkedRepo.objects.update_or_create(
        owner=org_name,
        repo_name=repo_name,
        img_url=request.POST.get('img_url'),
        user=request.user)
    return redirect('repositories:repo_overview')


@login_required
def unbookmark_repo(request, org_name, repo_name):
    BookmarkedRepo.objects.filter(owner=org_name, repo_name=repo_name, user=request.user).delete()
    return redirect('repositories:repo_overview')


def render_with_repositories(request, template_name, context, org=None, repo_name=None):
    repos = BookmarkedRepo.objects.filter(user=request.user)
    if len(repos) == 0 and template_name != 'repositories/overview.html':
        return redirect('repositories:repo_overview')
    bookmarked_repos_by_owner = {}
    for repo in repos:
        if repo.owner not in bookmarked_repos_by_owner:
            bookmarked_repos_by_owner[repo.owner] = []
        bookmarked_repos_by_owner[repo.owner].append(repo)

    context['bookmarked_repos'] = bookmarked_repos_by_owner
    context['repo_owner'] = org
    context['repo_name'] = repo_name
    context['selected_repo'] = f"{org}/{repo_name}"
    return render(request, template_name, context)


@login_required
def find_repositories(request):
    """Find Github repositories for the user."""
    g = Github(get_github_token(request), per_page=PAGE_SIZE)
    search_query = request.GET.get('query').replace(' ', '+').strip()
    if not search_query:
        return redirect('repositories:show_repo_picker')
    # First, try to see if the search query is a full repo name
    try:
        repo = g.get_user(request.user.username).get_repo(search_query)
        return render(request, 'repositories/repo_picker.html', {
            'search_query': search_query,
            'repositories': [repo],
            'total_page_count': 1,
            'current_page': 1,
            'page_buttons': [],
            'prev_page': 1,
            'next_page': 1,
        })
    except UnknownObjectException as e:
        # Repo not found, let's see if it's an org
        try:
            org = g.get_organization(search_query)
            repos = org.get_repos()
            return render_paginated_repo_picker(request, repos, repos.totalCount, search_query)
        except UnknownObjectException as e:
            # Not an org either, let's search for the query
            results = g.search_repositories(search_query, sort='updated', order='desc')
            return render_paginated_repo_picker(request, results, results.totalCount, search_query)