from django.shortcuts import render

from demo.github import list_repos_by_owner


def suite_overview(request, owner=None, repo=None):
    repos_by_owner = list_repos_by_owner()
    return render(request, "suite_overview.html", {
        "repos": repos_by_owner,
        "repo_owner": owner,
        "repo_name": repo,
        "selected_repo": f"{owner}/{repo}",
        "active_tab": "home",
    })


