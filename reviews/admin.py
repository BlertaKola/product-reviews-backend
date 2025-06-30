from django.contrib import admin
from .models import Review, ModerationResult, AIServiceError


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'text_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text', 'user__username']
    
    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = "Text Preview"


@admin.register(ModerationResult)
class ModerationResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'review_id', 'flagged', 'is_spam', 'spam_probability', 'created_at']
    list_filter = ['flagged', 'is_spam', 'created_at']
    search_fields = ['review__text', 'review__user__username']
    readonly_fields = ['created_at']


@admin.register(AIServiceError)
class AIServiceErrorAdmin(admin.ModelAdmin):
    list_display = ['id', 'service', 'error_preview', 'status_code', 'timestamp']
    list_filter = ['service', 'timestamp', 'status_code']
    search_fields = ['error_message', 'input_text']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Service Information', {
            'fields': ('service', 'status_code', 'timestamp')
        }),
        ('Error Details', {
            'fields': ('error_message', 'input_text'),
            'classes': ('wide',)
        }),
    )
    
    def error_preview(self, obj):
        return obj.error_message[:75] + "..." if len(obj.error_message) > 75 else obj.error_message
    error_preview.short_description = "Error Message Preview"
