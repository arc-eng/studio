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
    Decorator to ensure a valid API key is available for a user before executing a view function.

    This decorator performs the following actions:

    1. Checks for an existing API key in the user's profile.
    2. If missing, attempts to generate a new API key using the user's GitHub token.
    3. Redirects the user to the 'user_profile' page if an API key cannot be generated.
    4. Passes the API key to the view function as an additional argument if available.

    Args:
        view_func (function): The view function to be wrapped.

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
