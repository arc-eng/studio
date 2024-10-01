from django.urls import path

from . import views

urlpatterns = [
    path("new/", views.start_conversation, name="start_conversation"),
    path("<int:chat_id>/", views.view_chat, name="view_chat"),
    path("<int:chat_id>/delete/", views.delete_chat, name="delete_chat"),


]
