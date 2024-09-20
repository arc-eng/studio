import logging

from arcane.engine import ArcaneEngine
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import Report

logger = logging.getLogger(__name__)


def view_reports(request):
    reports = Report.objects.all()
    return render(request, "index.html", {
        "reports": reports,
        "active_tab": "reports",
    })


@require_POST
def generate_report(request):
    prompt = request.POST.get('prompt')
    engine = ArcaneEngine()
    task = engine.create_task("report_generation", prompt)
    report = Report.objects.create(prompt=prompt, task_id=task.id)
    return redirect(reverse('view_report', args=(report.id,)))


def view_report(request, report_id):
    report = Report.objects.get(id=report_id)
    engine = ArcaneEngine()
    task_status = engine.get_task_status(report.task_id)
    if task_status == 'completed':
        task_result = engine.get_task_result(report.task_id)
        report.result = task_result
        report.save()
    return render(request, "report_detail.html", {
        "report": report,
        "task_status": task_status,
    })
