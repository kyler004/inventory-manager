from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, LogoutView, ChangePasswordView, MeView

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth_login'), 
    path('logout/', LogoutView.as_view(), name='auth-logout'), 
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'), 
    path('password/change/', ChangePasswordView.as_view(), name='password-change'), 
    path('me/', MeView.as_view(), name='auth-me'), 
]