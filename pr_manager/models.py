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
