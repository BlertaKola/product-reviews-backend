from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} at {self.created_at}"



class ModerationResult(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='moderation_result')
    flagged = models.BooleanField()
    categories = models.JSONField()
    category_scores = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Moderation for Review {self.review.id} – Flagged: {self.flagged}"