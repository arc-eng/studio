from django.urls import path

from . import views

urlpatterns = [
    path("", views.show_repos, name="show_repos"),
    path("<str:owner>/<str:repo>/", views.show_repos, name="show_repo"),
    path("<str:owner>/<str:repo>/generate-description/", views.generate_description, name="generate_description"),
]
