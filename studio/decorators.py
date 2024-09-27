import logging
from functools import wraps

from arcane import ApiException
from arcane.engine import ArcaneEngine
from django.shortcuts import redirect
from django.urls import reverse

from studio.github import get_github_token

logger = logging.getLogger(__name__)


def needs_api_key(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Fetch the API key from the user's profile or another source
        api_key = request.user.api_key
        if not api_key:
            github_token = get_github_token(request)
            try:
                logger.info(f"Creating API key for user {request.user}")
                api_key = ArcaneEngine.create_api_key(github_token, "Arcane Studio (auto-generated)")
            except ApiException as e:
                logger.error(f"Failed to create API key: {e}")
            if api_key:
                request.user.api_key = api_key
                request.user.save()
        # If API key is not found, redirect to 'users:connect_engine'
        if not api_key:
            return redirect(reverse('user_profile'))

        # If API key is found, pass it to the view as an additional argument
        return view_func(request, api_key=api_key, *args, **kwargs)

    return _wrapped_view
