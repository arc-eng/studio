from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="pr_manager_home"),
    path("<str:owner>/<str:repo>/<int:pr_number>/<str:pr_tab>/", views.view_pull_request, name="view_pull_request"),
    path("<str:owner>/<str:repo>/<int:pr_number>/", views.view_pull_request, name="view_pull_request_default_tab"),
    path("<str:owner>/<str:repo>/", views.view_pull_request, name="view_pull_request_default"),
    path("generate-description/", views.generate_description, name="generate_description"),
    path("generate-review/", views.generate_review, name="generate_review"),
    path("apply-recommendation/", views.apply_recommendation, name="apply_review_finding_recommendation"),
    path("dismiss-recommendation/", views.dismiss_recommendation, name="dismiss_review_finding_recommendation"),
    path("apply-change-request/", views.apply_change_request, name="apply_pr_change_request"),
    path("comment-on-pr-review/", views.comment_on_pr_review, name="comment_on_pr_review"),
    path("reset-pr-review/", views.reset_pr_review, name="reset_pr_review"),
]
