from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AdminAgentListCreateView,
    AgentListView,
    CurrentUserView,
    LoginView,
    RegisterView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", CurrentUserView.as_view(), name="current_user"),
    path("agents/", AgentListView.as_view(), name="agents"),
    path("admin/agents/", AdminAgentListCreateView.as_view(), name="admin_agents"),
]
