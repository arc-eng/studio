from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from studio import settings
from .models import BookmarkedRepo
from github import Github

PAGE_SIZE = 10


def show_repo_picker(request, org_name=None):

    page = int(request.GET.get('page', 1))

    g = Github(settings.GITHUB_PAT, per_page=PAGE_SIZE)
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

    return render_with_repositories(request, 'repositories/repo_picker.html', {
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


def bookmark_repo(request, org_name, repo_name):
    if request.method == 'POST':
        BookmarkedRepo.objects.create(owner=org_name, repo_name=repo_name)
        return redirect('repositories:show_repo_picker_for_org', org_name=org_name)
    return redirect('repositories:show_repo_picker')


def render_with_repositories(request, template_name, context, org=None, repo_name=None):
    repos = BookmarkedRepo.objects.all()
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