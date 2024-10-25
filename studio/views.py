from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from github import Github

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
        'description': 'Imagine ChatGPT, but with access your code, wikis and other sources.',
        'link': reverse('chat_home')
    }, {
        'name': 'Tasks',
        'icon': 'fa-gears has-text-info-35',
        'description': 'A quick and easy way to hand off work to the engine.',
        'link': reverse('tasks_home')
    }, {
        'name': 'Pull Requests',
        'icon': 'fa-code-branch has-text-success-35',
        'description': 'Supports you in managing pull requests and code reviews.',
        'link': reverse('pr_manager_home')
    }, {
        'name': 'Build',
        'icon': 'fa-hammer has-text-danger-35',
        'description': 'One-click optimizations for build scripts and config files.',
        'link': reverse('build_home')
    }]
    return render(request, "how_it_works.html", {'tools': tools})


def studio_home(request):
    if request.user.is_authenticated:
        return render_with_repositories(request, "central.html", {
            "active_app": "home",
        }, None, None)
    return render(request, "studio_home.html", {
        "active_app": "home",
    })


def contribute(request, owner=None, repo=None):
    return render(request, "contribute.html", {
        "repo_owner": owner,
        "repo_name": repo,
        "selected_repo": f"{owner}/{repo}",
        "active_app": "contribute",
    })


@login_required
def user_logout(request):
    # Log out the user
    logout(request)
    return redirect(reverse("studio_home"))


def health_check(request):
    return HttpResponse("OK")