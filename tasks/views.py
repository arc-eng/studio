import json

from arcane import ApiException
from arcane.engine import ArcaneEngine
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from chat.models import ChatConversation, ChatMessage
from repositories.models import BookmarkedRepo
from repositories.views import render_with_repositories
from studio.decorators import needs_api_key


def home(request):
    if not request.user.is_authenticated:
        return render(request, "tasks_preview.html", {
            "active_app": "tasks",
        })
    return redirect("list_tasks", owner=None, repo=None)


@login_required
@needs_api_key
def view_task(request, owner, repo, task_id, api_key):
    task = ArcaneEngine(api_key).get_task(task_id)
    task_result = task.result
    try:
        json.loads(task_result)
        task_result = f"```json\n{task_result}\n```"
    except json.JSONDecodeError:
        pass
    return render_with_repositories(request, "view_task.html", {
        "task": task,
        "selected_repo": task.github_project,
        "active_app": "tasks",
        "task_result": task_result,
    }, owner, repo)


@login_required
@needs_api_key
def list_tasks(request, owner=None, repo=None, api_key=None):
    if not owner or owner == 'None':
        first_bookmark = BookmarkedRepo.objects.first()
        if first_bookmark:
            owner = first_bookmark.owner
            repo = first_bookmark.repo_name
        else:
            redirect('repositories:repo_overview')
    tasks = [t for t in ArcaneEngine(api_key).list_tasks() if t.github_project == f"{owner}/{repo}"]

    return render_with_repositories(request, "list_tasks.html", {
        "tasks": tasks,
        "active_app": "tasks",
    }, owner, repo)


@login_required
@require_POST
@needs_api_key
def create_task(request, owner, repo, api_key):
    if request.method == "POST":
        task_description = request.POST.get("task_description")
        if not task_description:
            raise ValueError("Task description is required.")
        else:
            try:
                task = ArcaneEngine(api_key).create_task(f"{owner}/{repo}", task_description)
            except ApiException as e:
                msg = str(e)
                if e.data and e.data.error:
                    msg = e.data.error
                return render(request, "error.html", {
                    "error": f"Failed to create task: {msg}",
                })
            return redirect('view_task', owner=owner, repo=repo, task_id=task.id)


@login_required
@require_POST
@needs_api_key
def create_followup_task(request, owner, repo, task_id, api_key=None):
    task = ArcaneEngine(api_key).get_task(task_id)

    chat = ChatConversation.objects.create(user=request.user,
                                           repo=BookmarkedRepo.objects.get(owner=owner, repo_name=repo, user=request.user))
    ChatMessage.objects.create(conversation=chat, message=task.user_request, task_id=task.id, result=task.result)
    chat.continue_conversation(request.POST.get('task_description'), api_key)

    return redirect(reverse('view_chat', args=[chat.id]))