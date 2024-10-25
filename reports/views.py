import logging

from arcane.engine import ArcaneEngine
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from repositories.views import render_with_repositories
from studio.decorators import needs_api_key
from studio.prompts import GENERATE_REPORT
from .models import Report

logger = logging.getLogger(__name__)


@login_required
def view_reports(request, owner, repo):
    reports = Report.objects.filter(repo=f"{owner}/{repo}").all()
    # Sorted by creation date
    reports = sorted(reports, key=lambda x: x.created_at, reverse=True)
    return render_with_repositories(request, "list_reports.html", {
        "reports": reports,
        "active_app": "reports",
    }, owner, repo)


@login_required
@require_POST
@needs_api_key
def generate_report(request, owner, repo, api_key):
    prompt = request.POST.get('prompt')
    title = request.POST.get('title')  # Get the title from the form
    engine = ArcaneEngine(api_key)
    task = engine.create_task(f"{owner}/{repo}", GENERATE_REPORT.format(report_description=prompt, title=title))
    report = Report.objects.create(prompt=prompt, task_id=task.id, title=title, repo=f"{owner}/{repo}")
    return redirect(reverse('view_report', args=(owner, repo, report.id,)))


@login_required
@needs_api_key
def view_report(request, owner, repo, report_id, api_key):
    report = Report.objects.get(id=report_id)
    engine = ArcaneEngine(api_key)
    task = engine.get_task(report.task_id)
    if task.status == "completed":
        report.result = task.result
        report.save()
        return render_with_repositories(request, "view_report.html", {
            "report": report,
            "task": task,
            "active_app": "reports",
        }, owner, repo)
    else:
        return render_with_repositories(request, "view_task.html", {
            "task": task,
            "active_app": "reports",
        }, owner, repo)
