"""
Health check and utility views.
"""
from django.db import connection
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


class HealthCheckView(APIView):
    """
    Health check endpoint for monitoring.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Check the health of the application services.
        """
        health_status = {
            'status': 'healthy',
            'database': self._check_database(),
            'cache': self._check_cache(),
        }

        # If any service is unhealthy, return 503
        if not all([health_status['database'], health_status['cache']]):
            health_status['status'] = 'unhealthy'
            return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(health_status, status=status.HTTP_200_OK)

    def _check_database(self):
        """Check database connectivity."""
        try:
            connection.ensure_connection()
            return True
        except Exception:
            return False

    def _check_cache(self):
        """Check cache connectivity."""
        try:
            cache.set('health_check', 'ok', 10)
            return cache.get('health_check') == 'ok'
        except Exception:
            return False
