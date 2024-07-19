from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from task_manager.models import Task
from task_manager.serializers import (
    CategorySerializer,
    CompleteTaskSerializer,
    RegisterSerializer,
    TaskSerializer,
)


class CreateCategoryView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        body = request.data

        serializer = CategorySerializer(data=body)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TasksView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        body = request.data

        serializer = TaskSerializer(data=body)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):  # Get current tasks
        tasks = Task.objects.filter(creator=request.user)
        serializer = TaskSerializer(tasks, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class EditDeleteGetTaskView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        if task.creator != request.user:
            return Response({"msg": "You don't have access"}, status=status.HTTP_403_FORBIDDEN)

        task_serializer = TaskSerializer(task)
        return Response(task_serializer.data)

    def delete(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        if task.creator != request.user:
            return Response({"msg": "You don't have access"}, status=status.HTTP_403_FORBIDDEN)

        task.delete()
        return Response(status=status.HTTP_200_OK)

    def patch(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        if task.creator != request.user:
            return Response({"msg": "You don't have access"}, status=status.HTTP_403_FORBIDDEN)

        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteTaskView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        body = request.data
        serializer = CompleteTaskSerializer(data=body)

        if serializer.is_valid():
            task = serializer.validated_data["task_id"]
            task.completed = True
            task.save()

            task_serializer = TaskSerializer(task)
            return Response(task_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user_response = serializer.save()
            return Response(user_response, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
