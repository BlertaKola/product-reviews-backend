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
    
    is_spam = models.BooleanField(default=False)
    spam_probability = models.FloatField(default=0.0)
    non_spam_probability = models.FloatField(default=1.0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Moderation for Review {self.review.id} – Flagged: {self.flagged}, Spam: {self.is_spam}"


class AIServiceError(models.Model):
    """
    Model to log errors from external AI services (moderation, spam detection)
    """
    
    SERVICE_CHOICES = [
        ('moderation', 'Moderation'),
        ('spam_detection', 'Spam Detection'),
    ]
    
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    input_text = models.TextField(help_text="The input that caused the error")
    error_message = models.TextField(help_text="The actual error message")
    status_code = models.IntegerField(null=True, blank=True, help_text="HTTP status code returned by the service")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "AI Service Error"
        verbose_name_plural = "AI Service Errors"
    
    def __str__(self):
        return f"{self.get_service_display()} Error at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"