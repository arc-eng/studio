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
from django.contrib import admin
from django.urls import path, include

import tasks.views
from studio import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("<str:owner>/<str:repo>/pull-request-manager/", include("pr_manager.urls")),
    path("<str:owner>/<str:repo>/tasks/", include("tasks.urls")),
    path("<str:owner>/<str:repo>/reports/", include("reports.urls")),
    path("repositories/", include("repositories.urls")),
    path("", views.studio_home, name="studio_home"),
    path("contribute/", views.contribute, name="contribute"),
    path('accounts/', include('allauth.urls')),
    path("login/", oauth2_login, name="github_login"),
    path("logout/", views.user_logout, name="user_logout"),
]
