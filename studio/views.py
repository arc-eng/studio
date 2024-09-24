from repositories.views import render_with_repositories


def studio_home(request, owner=None, repo=None):
    return render_with_repositories(request, "studio_home.html", {
        "repo_owner": owner,
        "repo_name": repo,
        "selected_repo": f"{owner}/{repo}",
        "active_tab": "home",
    })


def contribute(request, owner=None, repo=None):
    return render_with_repositories(request, "contribute.html", {
        "repo_owner": owner,
        "repo_name": repo,
        "selected_repo": f"{owner}/{repo}",
        "active_tab": "contribute",
    })