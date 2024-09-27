import logging
from typing import Optional

from allauth.socialaccount.models import SocialAccount, SocialToken

logger = logging.getLogger(__name__)


def get_github_token(request) -> Optional[str]:
    """Get the GitHub token for the current user."""
    if request.user.is_authenticated:
        # Check if the user has a connected GitHub account
        social_account = SocialAccount.objects.filter(user=request.user, provider='github').first()
        if social_account:
            # Get the GitHub token
            social_token = SocialToken.objects.filter(account__user=request.user).first()
            if social_token:
                return social_token.token  # This is the GitHub access token
    return None



