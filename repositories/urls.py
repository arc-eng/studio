from django.urls import path
from . import views

app_name = 'repositories'

urlpatterns = [
    path('', views.repo_overview, name='repo_overview'),
    path('select/', views.show_repo_picker, name='show_repo_picker'),
    path('<str:org_name>/', views.show_repo_picker, name='show_repo_picker_for_org'),
    path('orgs/<str:org_name>/repos/<str:repo_name>/bookmark/', views.bookmark_repo, name='bookmark_repo'),
    path('orgs/<str:org_name>/repos/<str:repo_name>/unbookmark/', views.unbookmark_repo, name='unbookmark_repo'),
]
