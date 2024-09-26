"""
URL configuration for studio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from allauth.socialaccount.providers.github.views import oauth2_login
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from studio import views
from studio.views import health_check

urlpatterns = [
    path("", health_check, name="health_check_root"),
    path("healthz/", health_check, name="health_check"),
    path('studio/', include([
        # Redirect default account login to GitHub login URL
        path(
            "accounts/login/",
            RedirectView.as_view(
                url=f"{settings.ROOT_PATH}/github/login/?process=login", permanent=True
            ),
        ),
        path('accounts/', include('allauth.urls')),
        path('admin/', admin.site.urls),
        path("<str:owner>/<str:repo>/pull-request-manager/", include("pr_manager.urls")),
        path("<str:owner>/<str:repo>/tasks/", include("tasks.urls")),
        path("<str:owner>/<str:repo>/reports/", include("reports.urls")),
        path("repositories/", include("repositories.urls")),
        path("", views.studio_home, name="studio_home"),
        path("contribute/", views.contribute, name="contribute"),
        path("login/", oauth2_login, name="github_login"),
        path("logout/", views.user_logout, name="user_logout"),
    ])),

]
