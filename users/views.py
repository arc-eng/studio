import logging

from arcane import ApiException
from arcane.engine import ArcaneEngine
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from build.models import BuildSystem
from chat.models import ChatConversation
from repositories.models import BookmarkedRepo
from studio.github import get_github_token

logger = logging.getLogger(__name__)


@login_required
def user_profile(request):

    api_key = request.user.api_key
    needs_engine_login = False
    if not api_key:
        github_token = get_github_token(request)
        try:
            logger.info(f"Creating API key for user {request.user}")
            api_key = ArcaneEngine.create_api_key(github_token, "Arcane Studio (auto-generated)")
            if api_key:
                request.user.api_key = api_key
                request.user.save()
        except ApiException as e:
            # Indicates the user hasn't used the engine yet
            logger.error(f"Failed to create API key: {e}")
            needs_engine_login = True

    return render(request, "user_profile.html", {
        "needs_engine_login": needs_engine_login,
        "active_app": "profile",
    })


@login_required
def delete_user_data(request):
    if request.method == "POST":
        ChatConversation.objects.filter(user=request.user).delete()
        BuildSystem.objects.filter(user=request.user).delete()
        BookmarkedRepo.objects.filter(user=request.user).delete()
        user = request.user
        user.delete()
        return redirect(reverse("studio_home"))

    return redirect(reverse("studio_home"))