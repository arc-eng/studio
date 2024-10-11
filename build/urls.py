from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="build_home"),
    path("<str:owner>/<str:repo>/", views.build_overview, name="build_overview"),
    path("apply-recommendation/", views.apply_recommendation, name="apply_recommendation"),
]
