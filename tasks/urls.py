from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="tasks_home"),
    path("<str:owner>/<str:repo>/", views.list_tasks, name="list_tasks"),
    path("<str:owner>/<str:repo>/create/", views.create_task, name="create_task"),
    path("<str:owner>/<str:repo>/<str:task_id>/", views.view_task, name="view_task"),
    path("<str:owner>/<str:repo>/<str:task_id>/follow-up/", views.create_followup_task, name="create_followup_task"),

]
