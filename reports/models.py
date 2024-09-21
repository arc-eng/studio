from django.db import models


class Report(models.Model):
    prompt = models.TextField()
    task_id = models.CharField(max_length=255)
    result = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    repo = models.CharField(max_length=255, null=True, blank=True)
