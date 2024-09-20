from django.urls import path

from . import views

urlpatterns = [
    path("", views.view_pull_requests, name="view_pull_requests"),
    path("generate-description/", views.generate_description, name="generate_description"),
]
