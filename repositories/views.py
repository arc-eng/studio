from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from github import Github

from studio.github import get_github_token
from .models import BookmarkedRepo

PAGE_SIZE = 10


@login_required
def show_repo_picker(request, org_name=None):

    page = int(request.GET.get('page', 1))

    g = Github(get_github_token(request), per_page=PAGE_SIZE)
    github_user = g.get_user()
    orgs = github_user.get_orgs()

    if not org_name:
        org_name = github_user.login

    if org_name == github_user.login:
        org_repos = github_user.get_repos(sort='pushed', direction='desc')
    else:
        org_repos = g.get_organization(org_name).get_repos(sort='pushed', direction='desc')

    page_count = int(org_repos.totalCount / PAGE_SIZE) + 1
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
        'selected_org': org_name,
        'orgs': [github_user, *orgs],
        'repositories': org_repos.get_page(page - 1),
        'github_user': github_user,
        'total_page_count': page_count,
        'current_page': page,
        'page_buttons': page_buttons,
        'prev_page': page - 1,
        'next_page': page + 1,
    })


@login_required
def repo_overview(request):
    return render_with_repositories(request, 'repositories/overview.html', {
        'active_tab': 'bookmarks',
    })


@login_required
def bookmark_repo(request, org_name, repo_name):
    BookmarkedRepo.objects.create(owner=org_name, repo_name=repo_name, user=request.user)
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