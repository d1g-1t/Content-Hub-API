"""
Views for user management.
"""
from django.contrib.auth.models import User
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    
    Public endpoint that allows new users to register.
    Returns user data and JWT tokens upon successful registration.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Create user and return tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens for the new user
        token_serializer = CustomTokenObtainPairSerializer(data={
            'username': user.username,
            'password': request.data['password']
        })
        token_serializer.is_valid(raise_exception=True)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': token_serializer.validated_data
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token view that uses our custom serializer.
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user profiles.
    
    list: Get all user profiles
    retrieve: Get a specific user profile
    me: Get current user's profile
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'username'
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user's profile.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """
        Update current user's profile.
        """
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)
