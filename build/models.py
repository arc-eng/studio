from django.db import models


class BuildSystem(models.Model):
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_update = models.DateTimeField(null=True)
    error = models.TextField(null=True, blank=True)
    user = models.ForeignKey("users.StudioUser", on_delete=models.CASCADE)
    repo = models.ForeignKey("repositories.BookmarkedRepo", on_delete=models.CASCADE)
    task_id = models.CharField(max_length=255, null=True, blank=True)

    @property
    def is_loading(self):
        return bool(self.task_id) and not bool(self.last_update)


class BuildSystemFile(models.Model):
    build_system = models.ForeignKey(BuildSystem, on_delete=models.CASCADE, related_name='files')
    path = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    purpose = models.TextField(blank=True)
    icon = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def github_link(self):
        return f"https://github.com/{self.build_system.repo.full_name}/blob/main/{self.path}"


class BuildSystemFileRecommendation(models.Model):
    build_system_file = models.ForeignKey(BuildSystemFile, on_delete=models.CASCADE, related_name='recommendations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    action = models.CharField(max_length=255)
    icon = models.CharField(max_length=255)
    benefit = models.TextField(blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True)
