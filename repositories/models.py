from django.db import models

class BookmarkedRepo(models.Model):
    owner = models.CharField(max_length=255)
    repo_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.owner}/{self.repo_name}"