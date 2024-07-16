from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from task_manager import views

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh_pair'),
    path('auth/signup/', views.RegisterView.as_view(), name='register'),
    path('tasks/', views.TasksView.as_view(), name='tasks'),
]
