from django.contrib.auth import logout
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


def user_logout(request):
    # Log out the user
    logout(request)
    # Redirect to home page (or any other page you prefer)
    return redirect("/")