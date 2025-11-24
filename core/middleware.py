"""
Custom middleware for the application.
"""
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('apps')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests with timing information.
    """
    
    def process_request(self, request):
        """Log request details and start timer."""
        request.start_time = time.time()
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
            }
        )
        return None

    def process_response(self, request, response):
        """Log response details with timing."""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(
                f"Request completed: {request.method} {request.path} - "
                f"Status: {response.status_code} - Duration: {duration:.2f}s",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration': duration,
                    'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
                }
            )
        return response
