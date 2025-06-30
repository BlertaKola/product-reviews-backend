from celery import shared_task
from .models import Review
from .services.moderation import moderate_review, save_moderation_result

@shared_task
def moderate_review_task(review_id):
    try:
        review = Review.objects.get(id=review_id)
        result = moderate_review(review.text)
        save_moderation_result(review, result)
    except Review.DoesNotExist:
        pass 