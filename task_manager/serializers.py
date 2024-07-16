from typing import Optional, Type, Dict, Any

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core import validators
from django.utils.deconstruct import deconstructible
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt import exceptions
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token, AccessToken, RefreshToken

from task_manager.models import Task, CustomUser, Category


@deconstructible
class UnicodeNameValidator(validators.RegexValidator):
    regex = r"^[\w.@+-]+\Z"
    message = ("Enter a valid first_name and last_name."
               " This value may contain only letters, numbers, and @/./+/-/_ characters.")
    flags = 0


class CategorySerializer(serializers.ModelSerializer):
    pass


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "email"]


class TaskSerializer(serializers.ModelSerializer):
    creator = CustomUserSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    title = serializers.CharField(max_length=200)
    body = serializers.CharField()
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(write_only=True, required=False, queryset=Category.objects.all())
    deadline = serializers.TimeField(allow_null=True, required=False)

    class Meta:
        model = Task
        fields = ["title", "creator", "created_at", "body", "category", "deadline", "category_id"]


class TokenObtainSerializer(serializers.Serializer):
    email_field = CustomUser.EMAIL_FIELD
    token_class: Optional[Type[Token]] = None

    default_error_messages = {
        "no_active_account": "No active account found with the given credentials"
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields[self.email_field] = serializers.CharField(write_only=True)
        self.fields["password"] = serializers.CharField(style={"input_type": "password"}, write_only=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[Any, Any]:
        authenticate_kwargs = {
            self.email_field: attrs[self.email_field],
            "password": attrs["password"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise exceptions.AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )

        return {}

    @classmethod
    def get_token(cls, user: CustomUser) -> Token:
        print(cls.token_class, type(cls.token_class))
        return cls.token_class.for_user(user)  # type: ignore


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    email = serializers.EmailField(
        required=True,
        write_only=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    username = serializers.CharField(required=True, write_only=True, max_length=50,
                                     validators=[UnicodeUsernameValidator, UniqueValidator(queryset=CustomUser.objects.all())])
    # first_name = serializers.CharField(required=True, max_length=50, validators=[UnicodeNameValidator])
    # last_name = serializers.CharField(required=True, max_length=50, validators=[UnicodeNameValidator])

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user: CustomUser = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            # first_name=validated_data['first_name'],
            # last_name=validated_data['last_name'],
        )

        user.set_password(validated_data['password'])
        user.save()

        user_data = CustomUserSerializer(user).data

        token = RefreshToken.for_user(user)
        tokens = {
            "access_token": str(token.access_token),
            "refresh_token": str(token),
        }

        response = {
            "user": user_data,
            "tokens": tokens,
        }
        return response

    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     user_data = CustomUserSerializer(response).data
    #
    #     token = RefreshToken.for_user(instance)
    #     tokens = {
    #         "access_token": str(token.access_token),
    #         "refresh_token": str(token),
    #     }
    #
    #     response.update({
    #         "user": user_data,
    #         "tokens": tokens,
    #     })
    #     return response
