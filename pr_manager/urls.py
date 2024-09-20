from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:owner>/<str:repo>/", views.index, name="show_repo"),
    path("<str:owner>/<str:repo>/generate-description/", views.generate_description, name="generate_description"),
]
