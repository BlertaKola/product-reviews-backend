import os
import requests
from reviews.models import Review, ModerationResult
from .spam import check_for_spam


def moderate_review(review_text):
    """
    Perform both OpenAI moderation and spam detection on review text
    Returns combined results from both services
    """
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
    moderation_result = response.json()
    
    try:
        is_spam, spam_probability, non_spam_probability = check_for_spam(review_text)
        if is_spam is None:
            is_spam = False
        if spam_probability is None:
            spam_probability = 0.0
        if non_spam_probability is None:
            non_spam_probability = 1.0
    except Exception as e:
        print(f"Spam detection failed: {e}")
        is_spam = False
        spam_probability = 0.0
        non_spam_probability = 1.0
    
    combined_result = {
        'openai_moderation': moderation_result,
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