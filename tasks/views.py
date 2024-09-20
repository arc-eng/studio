import markdown
from arcane.engine import ArcaneEngine
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from demo.github import list_repos_by_owner


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


def list_tasks(request, owner, repo):
    tasks = [t for t in ArcaneEngine().list_tasks() if t.github_project == f"{owner}/{repo}"]

    return render(request, "list_tasks.html", {
        "repos": list_repos_by_owner(),
        "repo_owner": owner,
        "repo_name": repo,
        "selected_repo": f"{owner}/{repo}",
        "tasks": tasks,
        "active_tab": "tasks",
    })


@require_POST
def create_task(request, owner, repo):
    if request.method == "POST":
        task_description = request.POST.get("task_description")
        if not task_description:
            raise ValueError("Task description is required.")
        else:
            task = ArcaneEngine().create_task(f"{owner}/{repo}", task_description)
            return redirect('view_task', owner=owner, repo=repo, task_id=task.id)
