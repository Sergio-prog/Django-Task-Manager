from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from task_manager import views

urlpatterns = [
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh_pair"),
    path("auth/signup/", views.RegisterView.as_view(), name="register"),
    path("tasks/", views.TasksView.as_view(), name="tasks"),
    path("categories/", views.CreateCategoryView.as_view(), name="categories"),
    path("tasks/<int:pk>/", views.EditDeleteGetTaskView.as_view(), name="delete_update_task"),
    path("tasks/complete/", views.CompleteTaskView.as_view(), name="complete_tasks"),
]
