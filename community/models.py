from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Community(models.Model):
    name = models.CharField(blank=True, max_length=300)
    members = models.ManyToManyField(User)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    requires_assistant = models.BooleanField(default=False)