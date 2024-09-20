from django.urls import path

from . import views

urlpatterns = [
    path("", views.view_reports, name="view_reports"),
    path("generate/", views.generate_report, name="generate_report"),
    path("<int:report_id>/", views.view_report, name="view_report"),
]
