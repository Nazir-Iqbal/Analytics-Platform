import os, io
from django.db import models
from projects.models import Project


def dataset_upload_path(instance, filename):
    return ''



class Dataset(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='datasets')
    name = models.CharField(max_length=200)
    file_name = models.CharField(max_length=255, default='dataset.csv')
    raw_data = models.TextField(blank=True, null=True)
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
        return self.file_name
