import os
from django.db import models
from projects.models import Project


def dataset_upload_path(instance, filename):
    return f'datasets/user_{instance.project.user_id}/project_{instance.project_id}/{filename}'


class Dataset(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='datasets')
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to=dataset_upload_path)
    rows = models.IntegerField(default=0)
    columns = models.IntegerField(default=0)
    column_names = models.JSONField(default=list)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

    def filename(self):
        return os.path.basename(self.file.name)
