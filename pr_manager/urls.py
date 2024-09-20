from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("generate-description/", views.generate_description, name="generate_description"),
]