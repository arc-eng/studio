from django.shortcuts import render

from demo.github import get_user_repos, list_repos_by_owner


def suite_overview(request, owner=None, repo=None):
    repos = get_user_repos()
    repos_by_owner = list_repos_by_owner()
    return render(request, "suite_overview.html", {
        "repos": repos_by_owner,
        "repo_count": repos.totalCount,
        "repo_owner": owner,
        "repo_name": repo,
        "selected_repo": f"{owner}/{repo}",
        "active_tab": "home",
    })


