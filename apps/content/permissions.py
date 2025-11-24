"""
Custom permissions for content app.
"""
from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors to edit their own objects.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission for this object."""
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only allowed for author
        return obj.author == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permissions."""
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if object has an 'author' or 'user' field
        owner = getattr(obj, 'author', None) or getattr(obj, 'user', None)
        return owner == request.user


class IsAuthenticatedOrReadOnlyCustom(permissions.BasePermission):
    """
    Custom permission that allows read access to everyone,
    but requires authentication for write operations.
    """
    
    def has_permission(self, request, view):
        """Check request-level permissions."""
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_authenticated
