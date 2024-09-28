from django.urls import path
from . import views

app_name = 'repositories'

urlpatterns = [
    path('', views.repo_overview, name='repo_overview'),
    path('select/', views.show_repo_picker, name='show_repo_picker'),
    path('search/', views.find_repositories, name='find_repositories'),
    path('orgs/<str:org_name>/repos/<str:repo_name>/bookmark/', views.bookmark_repo, name='bookmark_repo'),
    path('orgs/<str:org_name>/repos/<str:repo_name>/unbookmark/', views.unbookmark_repo, name='unbookmark_repo'),
]
