from django.db import models


class PullRequestDescription(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey("users.StudioUser", on_delete=models.CASCADE)
    repo = models.ForeignKey("repositories.BookmarkedRepo", on_delete=models.CASCADE)
    pr_number = models.IntegerField(null=False)
    description = models.TextField(max_length=255, null=False, blank=False)
    task_id = models.CharField(max_length=255, null=True, blank=True)


class ReviewFinding(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    review = models.ForeignKey("PullRequestReview", on_delete=models.CASCADE, related_name="findings")
    task_id = models.CharField(max_length=255, null=True, blank=True)
    file = models.CharField(max_length=255, null=True, blank=True)
    issue = models.TextField(null=True, blank=True)
    criticality = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    line_start = models.IntegerField(null=True, blank=True)
    line_end = models.IntegerField(null=True, blank=True)
    recommendation = models.TextField(null=True, blank=True)


class PullRequestReview(models.Model):
    user = models.ForeignKey("users.StudioUser", on_delete=models.CASCADE)
    repo = models.ForeignKey("repositories.BookmarkedRepo", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    pr_number = models.IntegerField(null=False)
    updated_at = models.DateTimeField(auto_now=True)
    summary = models.TextField(null=True, blank=False)
    task_id = models.CharField(max_length=255, null=True, blank=True)
