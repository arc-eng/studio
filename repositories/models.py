from django.db import models


class BookmarkedRepo(models.Model):
    owner = models.CharField(max_length=255)
    repo_name = models.CharField(max_length=255)
    user = models.ForeignKey("users.StudioUser", on_delete=models.CASCADE)
    img_url = models.CharField(max_length=255, blank=True, null=True)

    @property
    def full_name(self):
        return f"{self.owner}/{self.repo_name}"

    def __str__(self):
        return f"{self.owner}/{self.repo_name}"