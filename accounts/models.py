from django.db import models
from django.contrib.auth.models import User
import secrets


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    api_key = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def regenerate_api_key(self):
        self.api_key = secrets.token_hex(32)
        self.save()

    def __str__(self):
        return self.user.username
from django.db import models

# Create your models here.
