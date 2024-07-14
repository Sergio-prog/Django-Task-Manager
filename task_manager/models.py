from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Task:
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200)
    body = models.TextField()
