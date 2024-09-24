from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import BookmarkedRepo
from github import Github

@login_required
def list_orgs(request):
    g = Github(request.user.social_auth.get(provider='github').extra_data['access_token'])
    orgs = g.get_user().get_orgs()
    return render(request, 'repositories/list_orgs.html', {'orgs': orgs})

@login_required
def list_repos(request, org_name):
    g = Github(request.user.social_auth.get(provider='github').extra_data['access_token'])
    org = g.get_organization(org_name)
    repos = org.get_repos()
    return render(request, 'repositories/list_repos.html', {'repos': repos, 'org_name': org_name})

@login_required
def bookmark_repo(request, org_name, repo_name):
    if request.method == 'POST':
        BookmarkedRepo.objects.create(owner=org_name, repo_name=repo_name)
        return redirect('repositories:list_orgs')
    return redirect('repositories:list_repos', org_name=org_name)