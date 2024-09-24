from django.urls import path
from . import views

app_name = 'repositories'

urlpatterns = [
    path('', views.list_orgs, name='list_orgs'),
    path('orgs/<str:org_name>/repos/', views.list_repos, name='list_repos'),
    path('orgs/<str:org_name>/repos/<str:repo_name>/bookmark/', views.bookmark_repo, name='bookmark_repo'),
]