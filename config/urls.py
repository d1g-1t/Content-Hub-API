"""
URL configuration for Content Hub API.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from core.views import HealthCheckView

# API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Content Hub API",
        default_version='v1',
        description="""
        A modern, production-ready RESTful API for content management.
        
        Features:
        - JWT Authentication
        - Article & Comment Management
        - Advanced Filtering & Search
        - Rate Limiting
        - Caching
        - Comprehensive Documentation
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="api@contenthub.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health Check
    path('health/', HealthCheckView.as_view(), name='health-check'),
    
    # API v1
    path('api/v1/', include([
        # Authentication
        path('auth/', include([
            path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
            path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
            path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
        ])),
        
        # Apps
        path('users/', include('apps.users.urls')),
        path('content/', include('apps.content.urls')),
    ])),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# Debug toolbar (development only)
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Static and media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
