"""
URL configuration for users app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserRegistrationView,
    CustomTokenObtainPairView,
    UserProfileViewSet
)

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('', include(router.urls)),
]
