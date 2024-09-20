from django.urls import path

from . import views

urlpatterns = [
    path("", views.repo_list, name="repo_list"),
    path("<str:owner>/<str:repo>/", views.index, name="index"),
    path("generate-description/", views.generate_description, name="generate_description"),
]
