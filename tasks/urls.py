from django.urls import path

from . import views

urlpatterns = [
    path("", views.list_tasks, name="list_tasks"),
    path("<str:task_id>/", views.view_task, name="view_task"),
]
