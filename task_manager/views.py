from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics
from rest_framework_simplejwt.views import TokenViewBase

from task_manager.models import CustomUser
from task_manager.serializers import TaskSerializer, RegisterSerializer, TokenObtainSerializer


# Create your views here.
class TasksView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        body = request.data
        body["creator"] = request.user

        serializer = TaskSerializer(data=body)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user_response = serializer.save()
            return Response(user_response, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TasksView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save(creator=request.user)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

