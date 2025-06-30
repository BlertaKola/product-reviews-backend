import os
import requests
from reviews.models import Review, ModerationResult


def moderate_review(review_text):
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
    return moderation_result


def save_moderation_result(review, moderation_result):
    categories = moderation_result['results'][0]['categories']
    
    ModerationResult.objects.create(
        review=review,
        flagged=moderation_result['results'][0]['flagged'],
        categories=categories,
        category_scores=moderation_result['results'][0]['category_scores'],
    )



def get_moderation_result(review_id):
    try:
        return ModerationResult.objects.get(review_id=review_id)
    except ModerationResult.DoesNotExist:
        return None