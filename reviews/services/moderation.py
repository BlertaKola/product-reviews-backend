import os
import requests
from reviews.models import Review, ModerationResult
from .spam import check_for_spam
from ..utils import log_ai_error


def moderate_review(review_text):
    """
    Perform both OpenAI moderation and spam detection on review text
    Returns combined results from both services
    """
    # OpenAI moderation
    openai_result = None
    try:
        url = "https://api.openai.com/v1/moderations"
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json",
        }
        payload = {
            "input": review_text,
            "model": "omni-moderation-latest"
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        openai_result = response.json()
        
    except requests.RequestException as e:
        # Log the moderation error
        log_ai_error('moderation', review_text, e)
        # Use safe defaults for OpenAI moderation
        openai_result = {
            'results': [{
                'flagged': False,
                'categories': {},
                'category_scores': {}
            }]
        }
    except Exception as e:
        # Log unexpected errors
        log_ai_error('moderation', review_text, f"Unexpected error: {e}")
        # Use safe defaults
        openai_result = {
            'results': [{
                'flagged': False,
                'categories': {},
                'category_scores': {}
            }]
        }
    
    # Spam detection with error handling
    try:
        is_spam, spam_probability, non_spam_probability = check_for_spam(review_text)
        # Ensure we have valid values
        if is_spam is None:
            is_spam = False
        if spam_probability is None:
            spam_probability = 0.0
        if non_spam_probability is None:
            non_spam_probability = 1.0
    except Exception as e:
        # Log spam detection error
        log_ai_error('spam_detection', review_text, e)
        print(f"Spam detection failed: {e}")
        is_spam = False
        spam_probability = 0.0
        non_spam_probability = 1.0
    
    # Combine results
    combined_result = {
        'openai_moderation': openai_result,
        'spam_detection': {
            'is_spam': is_spam,
            'spam_probability': spam_probability,
            'non_spam_probability': non_spam_probability
        }
    }
    
    return combined_result


def save_moderation_result(review, combined_result):
    """
    Save both OpenAI moderation and spam detection results
    """
    openai_result = combined_result['openai_moderation']
    spam_result = combined_result['spam_detection']
    
    categories = openai_result['results'][0]['categories']
    
    is_spam = spam_result.get('is_spam', False)
    spam_probability = spam_result.get('spam_probability', 0.0)
    non_spam_probability = spam_result.get('non_spam_probability', 1.0)
    
    if is_spam is None or not isinstance(is_spam, bool):
        is_spam = False
    if spam_probability is None or not isinstance(spam_probability, (int, float)):
        spam_probability = 0.0
    if non_spam_probability is None or not isinstance(non_spam_probability, (int, float)):
        non_spam_probability = 1.0
    
    print(f"Creating ModerationResult with: is_spam={is_spam}, spam_prob={spam_probability}, non_spam_prob={non_spam_probability}")
    
    ModerationResult.objects.create(
        review=review,
        flagged=openai_result['results'][0]['flagged'],
        categories=categories,
        category_scores=openai_result['results'][0]['category_scores'],
        is_spam=is_spam,
        spam_probability=float(spam_probability),
        non_spam_probability=float(non_spam_probability),
    )


def get_moderation_result(review_id):
    try:
        return ModerationResult.objects.get(review_id=review_id)
    except ModerationResult.DoesNotExist:
        return None