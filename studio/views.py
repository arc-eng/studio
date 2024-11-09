from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from github import Github
from github.GithubException import GithubException

from repositories.models import BookmarkedRepo
from repositories.views import render_with_repositories
from studio.github import get_github_token


def terms_of_service(request):
    return render(request, "legal/terms_of_service.html")


def privacy_policy(request):
    return render(request, "legal/privacy_policy.html")

def code_policy(request):
    return render(request, "legal/code_policy.html")


def how_it_works(request):
    tools = [{
        'name': 'Chat',
        'icon': 'fa-comment',
        'description': 'Analyze issues, workshop ideas, generate content',
        'link': reverse('chat_home')
    }, {
        'name': 'Tasks',
        'icon': 'fa-gears has-text-info-35',
        'description': 'A quick and easy way to hand off work to the engine',
        'link': reverse('tasks_home')
    }, {
        'name': 'PRs',
        'icon': 'fa-code-branch has-text-success-35',
        'description': 'Supports you in managing pull requests and code reviews',
        'link': reverse('pr_manager_home')
    }, {
        'name': 'Build',
        'icon': 'fa-hammer has-text-danger-35',
        'description': 'One-click optimizations for build scripts and config files',
        'link': reverse('build_home')
    }]
    return render(request, "how_it_works.html", {'tools': tools})


def studio_home(request, owner=None, repo=None):
    if request.user.is_authenticated:
        if not owner or owner == 'None':
            first_bookmark = BookmarkedRepo.objects.filter(user=request.user).first()
            if first_bookmark:
                owner = first_bookmark.owner
                repo = first_bookmark.repo_name
                return redirect('studio_home_repo', owner=owner, repo=repo)
            else:
                return redirect('repositories:repo_overview')
        try:
            g = Github(get_github_token(request))
            pull_requests = g.get_repo(f"{owner}/{repo}").get_pulls(state='open')
        except GithubException as e:
            if e.status == 401:
                return redirect(reverse('user_logout'))
            else:
                return render(request, "error.html", {
                    "error": str(e),
                })

        return render_with_repositories(request, "central.html", {
            "pull_requests": pull_requests if pull_requests.totalCount > 0 else None,
            "active_app": "home",
        }, owner, repo)

    return render(request, "studio_home.html", {
        "active_app": "home",
    })


def contribute(request):
    return render(request, "contribute.html", {
        "active_app": "contribute",
    })


@login_required
def user_logout(request):
    # Log out the user
    logout(request)
    return redirect(reverse("studio_home"))


def health_check(request):
    return HttpResponse("OK")