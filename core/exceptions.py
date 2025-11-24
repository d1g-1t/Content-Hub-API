"""
Custom exception handler for the API.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Log the exception
        logger.error(
            f"API Exception: {exc.__class__.__name__} - {str(exc)}",
            exc_info=True,
            extra={'context': context}
        )

        # Customize the response data
        custom_response_data = {
            'error': {
                'message': str(exc),
                'status_code': response.status_code,
                'details': response.data if isinstance(response.data, dict) else {'detail': response.data}
            }
        }
        
        response.data = custom_response_data

    return response


class ValidationError(Exception):
    """Custom validation error."""
    pass


class BusinessLogicError(Exception):
    """Custom business logic error."""
    pass
