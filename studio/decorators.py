import logging
import os
from functools import wraps

from arcane import ApiException
from arcane.engine import ArcaneEngine
from django.shortcuts import redirect
from django.urls import reverse

from studio.github import get_github_token

logger = logging.getLogger(__name__)


def needs_api_key(view_func):
    """
    Decorator to ensure a valid API key is available for a view function.

    This decorator attempts to retrieve an API key from the user's profile. If the API key is not present,
    it tries to create one using the ArcaneEngine with a GitHub token. If successful, the API key is saved
    to the user's profile. If an API key cannot be found or created, the user is redirected to a profile
    page to connect their account to the Arcane Engine. If an API key is available, it is set as an
    environment variable and passed to the view function.

    Args:
        view_func (function): The view function to be decorated.

    Returns:
        function: The wrapped view function with API key handling.
    """
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
        os.environ.setdefault('ARCANE_API_KEY', api_key)
        return view_func(request, api_key=api_key, *args, **kwargs)

    return _wrapped_view
