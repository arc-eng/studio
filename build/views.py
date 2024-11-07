import json
import logging
from typing import List

import arcane
from arcane.engine import ArcaneEngine
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from pydantic import BaseModel, Field
from pydantic_core import from_json

from build.models import BuildSystem, BuildSystemFile, BuildSystemFileRecommendation
from build.prompts import DISCOVER_BUILD_FILES, APPLY_RECOMMENDATION
from repositories.models import BookmarkedRepo
from repositories.views import render_with_repositories
from studio.decorators import needs_api_key
from studio.util import handle_engine_api_exception

logger = logging.getLogger(__name__)


class FileRecommendation(BaseModel):
    action: str = Field(title="Call to action", description="Action to be taken")
    icon: str = Field(title="Icon", description="FontAwesome icon class to represent the action")
    benefit: str = Field(title="Benefit", description="The benefit of taking this action")


class BuildSystemFileDescription(BaseModel):
    path: str = Field(title="File path", description="Path of the file in the repo")
    purpose: str = Field(title="Purpose", description="What is the purpose of this file")
    icon: str = Field(title="Icon", description="FontAwesome icon class to represent this file")
    title: str = Field(title="Title", description="Display title for the file")
    recommendations: List[FileRecommendation] = Field(title="Recommendations", description="Recommendations for this file")


class BuildSystemDescription(BaseModel):
    description: str = Field(title="Description", description="A description of the build setup")
    files: List[BuildSystemFileDescription] = Field(title="Files", description="Files in the build setup")


def home(request):
    if not request.user.is_authenticated:
        return render(request, "build_preview.html", {
            "active_app": "build",
        })
    return redirect("build_overview", owner=None, repo=None)


@login_required
@needs_api_key
def build_overview(request, owner=None, repo=None, api_key=None):
    if not owner or owner == 'None':
        first_bookmark = BookmarkedRepo.objects.filter(user=request.user).first()
        if first_bookmark:
            owner = first_bookmark.owner
            repo = first_bookmark.repo_name
            return redirect('build_overview', owner=owner, repo=repo)
        else:
            return redirect('repositories:repo_overview')
    bookmark = BookmarkedRepo.objects.filter(user=request.user, owner=owner, repo_name=repo).first()
    if not bookmark:
        return render(request, "error.html", {"error": "Repository not found or unauthorized access"})
    task = None
    # Create a build system instance for the repo if not exists
    system:BuildSystem = BuildSystem.objects.filter(user=request.user, repo=bookmark).first()
    if not system:
        system = BuildSystem.objects.create(user=request.user, repo=bookmark)
    if not system.task_id:
        # Run task to collect build system information
        task = ArcaneEngine(api_key).create_task(f"{owner}/{repo}", DISCOVER_BUILD_FILES,
                                                 output_format="json",
                                                 output_structure=json.dumps(BuildSystemDescription.model_json_schema()))
        system.task_id = task.id
        system.save()
    elif not system.last_update:
        # Task was created, but we haven't saved a result yet
        task = ArcaneEngine(api_key).get_task(system.task_id)
        if task.status == "completed":
            try:
                description = BuildSystemDescription.model_validate(from_json(task.result))
                logger.info(f"Successfully generated build system description for {task.github_project}")
                system.description = description.description
                for file_description in description.files:
                    file = BuildSystemFile.objects.create(
                        path=file_description.path, icon=file_description.icon, build_system=system,
                        purpose=file_description.purpose, title=file_description.title
                    )
                    for rec_description in file_description.recommendations:
                        BuildSystemFileRecommendation.objects.create(
                            build_system_file=file, action=rec_description.action, icon=rec_description.icon,
                            benefit=rec_description.benefit
                        )
                system.last_update = timezone.now()
                system.save()
            except ValueError as e:
                logger.error("Failed to parse task result", exc_info=e)
                system.error = f"Failed to parse task result: {str(e)}"
        elif task.status == "failed":
            system.error = task.result
            system.save()

    return render_with_repositories(request, "build_home.html", {
        "task": task,
        "active_app": "build",
        "system": system
    }, owner, repo)


@login_required
@require_POST
def reset_build_system(request):
    system_id = request.POST.get('system_id')
    system = BuildSystem.objects.get(pk=system_id)
    if system.user != request.user:
        return render(request, "error.html", {"error": "Unauthorized"})
    owner = system.repo.owner
    repo = system.repo.repo_name
    system.delete()
    return redirect('build_overview', owner=owner, repo=repo)


@login_required
@require_POST
@needs_api_key
def apply_recommendation(request, api_key):
    try:
        recommendation_id = request.POST.get('recommendation_id')
        recommendation = BuildSystemFileRecommendation.objects.get(pk=recommendation_id)
    except BuildSystemFileRecommendation.DoesNotExist:
        return render(request, "error.html", {"error": "Recommendation not found"})
    if not request.user.id == recommendation.build_system_file.build_system.user.id:
        return render(request, "error.html", {"error": "Unauthorized"})



    engine = ArcaneEngine(api_key)
    prompt = APPLY_RECOMMENDATION.format(path=recommendation.build_system_file.path,
                                         changes=recommendation.action,
                                         goal=recommendation.benefit)
    try:
        repo = recommendation.build_system_file.build_system.repo
        task = engine.create_task(repo.full_name, prompt)
        recommendation.task_id = task.id
        recommendation.save()
    except arcane.exceptions.ApiException as e:
        return handle_engine_api_exception(request, e, repo.owner, repo.repo_name)

    return redirect(reverse('view_task', args=(repo.owner, repo.repo_name, task.id,)))


