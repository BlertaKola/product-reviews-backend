"""
Utility functions for the reviews app
"""
from .models import AIServiceError
import logging

logger = logging.getLogger(__name__)


def log_ai_error(service, input_text, error, status_code=None):
    """
    Log an AI service error to the database and optionally to the Django logger.
    
    Args:
        service (str): The service that failed ('moderation' or 'spam_detection')
        input_text (str): The input text that caused the error
        error (Exception or str): The error object or error message
        status_code (int, optional): HTTP status code if available
    
    Returns:
        AIServiceError: The created error record
    
    Example:
        try:
            # some API call
            response = requests.post(...)
        except requests.RequestException as e:
            log_ai_error('spam_detection', review_text, e, status_code=500)
    """
    
    if hasattr(error, 'response') and hasattr(error.response, 'text'):
        error_message = f"{str(error)} - Response: {error.response.text}"
        if not status_code and hasattr(error.response, 'status_code'):
            status_code = error.response.status_code
    elif hasattr(error, 'args') and error.args:
        error_message = str(error)
    else:
        error_message = str(error)
    
    truncated_input = input_text[:1000] + "..." if len(input_text) > 1000 else input_text
    
    try:
        ai_error = AIServiceError.objects.create(
            service=service,
            input_text=truncated_input,
            error_message=error_message,
            status_code=status_code
        )
        
        logger.error(
            f"AI Service Error - {service}: {error_message} "
            f"(Status: {status_code}) for input: {truncated_input[:100]}..."
        )
        
        return ai_error
        
    except Exception as db_error:
        logger.error(
            f"Failed to log AI service error to database: {db_error}. "
            f"Original error - {service}: {error_message}"
        )
        return None


def get_recent_ai_errors(service=None, limit=10):
    """
    Get recent AI service errors for monitoring/debugging.
    
    Args:
        service (str, optional): Filter by service type ('moderation' or 'spam_detection')
        limit (int): Maximum number of errors to return
    
    Returns:
        QuerySet: Recent AIServiceError objects
    """
    queryset = AIServiceError.objects.all()
    
    if service:
        queryset = queryset.filter(service=service)
    
    return queryset[:limit] 