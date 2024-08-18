from typing import Any, Dict, Optional, Type

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core import validators
from django.shortcuts import get_object_or_404
from django.utils.deconstruct import deconstructible
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt import exceptions
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, Token

from task_manager.fields import EnumField
from task_manager.models import Category, CustomUser, Task, TaskPriority


@deconstructible
class UnicodeNameValidator(validators.RegexValidator):
    regex = r"^[\w.@+-]+\Z"
    message = (
        "Enter a valid first_name and last_name."
        " This value may contain only letters, numbers, and @/./+/-/_ characters."
    )
    flags = 0


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "email"]


class CategorySerializer(serializers.ModelSerializer):
    creator = CustomUserSerializer(read_only=True)
    name = serializers.CharField(max_length=200)

    class Meta:
        model = Category
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    creator = CustomUserSerializer(read_only=True)
    assigned_to = CustomUserSerializer(read_only=True)
    assigned_to_username = serializers.CharField(required=False, write_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    title = serializers.CharField(max_length=200)
    body = serializers.CharField(required=False)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        write_only=True, required=False, queryset=Category.objects.all(), source="category"
    )
    deadline = serializers.TimeField(allow_null=True, required=False)
    priority = EnumField(enum=TaskPriority, default=TaskPriority.MEDIUM)
    completed = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        assigned_to_username = validated_data.pop("assigned_to_username", None)
        if assigned_to_username:
            assigned_to_user = get_object_or_404(CustomUser, username=assigned_to_username)
            validated_data["assigned_to"] = assigned_to_user

        # validated_data["creator"] = self.context['request'].user
        task = Task.objects.create(**validated_data)
        return task

    def update(self, instance, validated_data):
        assigned_to_username = validated_data.pop("assigned_to_username", None)
        if assigned_to_username:
            assigned_to_user = get_object_or_404(CustomUser, username=assigned_to_username)
            validated_data["assigned_to"] = assigned_to_user

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "creator",
            "created_at",
            "body",
            "category",
            "deadline",
            "category_id",
            "assigned_to",
            "assigned_to_username",
            "priority",
            "completed",
        ]


class CompleteTaskSerializer(serializers.Serializer):
    task_id = serializers.PrimaryKeyRelatedField(write_only=True, required=True, queryset=Task.objects.all())


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    email = serializers.EmailField(
        required=True, write_only=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        write_only=True,
        max_length=50,
        validators=[UnicodeUsernameValidator, UniqueValidator(queryset=CustomUser.objects.all())],
    )

    # first_name = serializers.CharField(required=True, max_length=50, validators=[UnicodeNameValidator])
    # last_name = serializers.CharField(required=True, max_length=50, validators=[UnicodeNameValidator])

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user: CustomUser = CustomUser.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            # first_name=validated_data['first_name'],
            # last_name=validated_data['last_name'],
        )

        user.set_password(validated_data["password"])
        user.save()

        user_data = CustomUserSerializer(user).data

        token: RefreshToken = RefreshToken.for_user(user)  # type: ignore
        tokens = {
            "access_token": str(token.access_token),
            "refresh_token": str(token),
        }

        response = {
            "user": user_data,
            "tokens": tokens,
        }
        return response
