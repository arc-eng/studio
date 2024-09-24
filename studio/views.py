from django.shortcuts import render

from studio.github import list_repos_by_owner, get_cached_user


def studio_home(request, owner=None, repo=None):
    repos_by_owner = list_repos_by_owner()
    return render(request, "studio_home.html", {
        "repos": repos_by_owner,
        "repo_owner": owner,
        "repo_name": repo,
        "selected_repo": f"{owner}/{repo}",
        "active_tab": "home",
    })


def select_repository(request, owner=None, repo=None):
    user = get_cached_user()
    orgs = user.get_orgs()
    if owner:
        repos = user.get_repos()
        return render(request, "select_repository.html", {
            "repos": repos,
            "repo_owner": owner,
            "repo_name": repo,
            "selected_repo": f"{owner}/{repo}",
            "active_tab": "repos",
        })
    return render(request, "select_repository.html", {
        "orgs": orgs,
        "active_tab": "orgs",
    })