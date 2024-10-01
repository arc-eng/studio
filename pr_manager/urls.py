from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="pr_manager_home"),
    path("<str:owner>/<str:repo>/", views.view_pull_requests, name="view_pull_requests"),
    path("<str:owner>/<str:repo>/generate-description/", views.generate_description, name="generate_description"),
]
