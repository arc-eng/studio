from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render


def studio_home(request, owner=None, repo=None):
    return render(request, "studio_home.html", {
        "repo_owner": owner,
        "repo_name": repo,
        "selected_repo": f"{owner}/{repo}",
        "active_tab": "home",
    })


def contribute(request, owner=None, repo=None):
    return render(request, "contribute.html", {
        "repo_owner": owner,
        "repo_name": repo,
        "selected_repo": f"{owner}/{repo}",
        "active_tab": "contribute",
    })


@login_required
def user_logout(request):
    # Log out the user
    logout(request)
    # Redirect to home page (or any other page you prefer)
    return redirect("/")


@login_required
def user_profile(request):
    return render(request, "user_profile.html", {
        "active_tab": "profile",
    })


def health_check(request):
    return HttpResponse("OK")