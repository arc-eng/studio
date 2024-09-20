import markdown
from arcane.engine import ArcaneEngine
from django.shortcuts import render

from demo.github import get_user_repos, list_repos_by_owner, get_prs


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


def view_task(request, owner, repo, task_id):
    task = ArcaneEngine().get_task(task_id)
    task.result = markdown.markdown(task.result)
    task.user_request = markdown.markdown(task.user_request)
    repo_owner, repo_name = task.github_project.split('/')
    return render(request, "view_task.html", {
        "repos": list_repos_by_owner(),
        "task": task,
        "repo_owner": repo_owner,
        "repo_name": repo_name,
        "selected_repo": task.github_project,
        "active_tab": "tasks",
    })

