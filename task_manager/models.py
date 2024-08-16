from enum import Enum, IntEnum

from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class TaskPriority(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2


class Task(models.Model):
    priority_choices = [(el.value, el.name) for el in TaskPriority]

    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="creators")
    assigned_to = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, default=None, related_name="assigned_to_users"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    body = models.TextField(null=True, default=None)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, default=None)
    deadline = models.DateTimeField(default=None, null=True)
    priority = models.CharField(choices=priority_choices, default=TaskPriority.MEDIUM)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
