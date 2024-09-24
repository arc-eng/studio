import logging

from arcane.engine import ArcaneEngine
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from studio.github import list_repos_by_owner
from studio.prompts import GENERATE_REPORT
from .models import Report

logger = logging.getLogger(__name__)


def view_reports(request, owner, repo):
    reports = Report.objects.filter(repo=f"{owner}/{repo}").all()
    # Sorted by creation date
    reports = sorted(reports, key=lambda x: x.created_at, reverse=True)
    return render(request, "list_reports.html", {
        "reports": reports,
        "repos": list_repos_by_owner(),
        "repo_owner": owner,
        "repo_name": repo,
        "selected_repo": f"{owner}/{repo}",
        "active_tab": "reports",
    })


@require_POST
def generate_report(request, owner, repo):
    prompt = request.POST.get('prompt')
    title = request.POST.get('title')  # Get the title from the form
    engine = ArcaneEngine()
    task = engine.create_task(f"{owner}/{repo}", GENERATE_REPORT.format(report_description=prompt, title=title))
    report = Report.objects.create(prompt=prompt, task_id=task.id, title=title, repo=f"{owner}/{repo}")
    return redirect(reverse('view_report', args=(owner, repo, report.id,)))


def view_report(request, owner, repo, report_id):
    report = Report.objects.get(id=report_id)
    engine = ArcaneEngine()
    task = engine.get_task(report.task_id)
    if task.status == "completed":
        report.result = task.result
        report.save()
        return render(request, "view_report.html", {
            "report": report,
            "repos": list_repos_by_owner(),
            "task": task,
            "repo_owner": owner,
            "repo_name": repo,
            "selected_repo": f"{owner}/{repo}",
            "active_tab": "reports",
        })
    else:
        return render(request, "view_task.html", {
            "repos": list_repos_by_owner(),
            "task": task,
            "repo_owner": owner,
            "repo_name": repo,
            "selected_repo": task.github_project,
            "active_tab": "reports",
        })
