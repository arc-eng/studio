from django.urls import path
from . import views

app_name = 'repositories'

urlpatterns = [
    path('', views.repo_overview, name='repo_overview'),
    path('select/', views.show_repo_picker, name='show_repo_picker'),
    path('search/', views.find_repositories, name='find_repositories'),
    path('install/<str:owner_name>/<str:repo_name>/', views.install_repo, name='install_repo'),
    path('orgs/<str:owner_name>/repos/<str:repo_name>/bookmark/', views.bookmark_repo, name='bookmark_repo'),
    path('orgs/<str:owner_name>/repos/<str:repo_name>/unbookmark/', views.unbookmark_repo, name='unbookmark_repo'),
]
