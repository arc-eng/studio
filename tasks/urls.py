from django.urls import path

from . import views

urlpatterns = [
    path("", views.list_tasks, name="list_tasks"),
    path("create/", views.create_task, name="create_task"),
    path("<str:task_id>/", views.view_task, name="view_task"),
    path("<str:task_id>/follow-up/", views.create_followup_task, name="create_followup_task"),

]
