from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from reviews.models import Review, ModerationResult, AIServiceError

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        return attrs
    


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'text', 'created_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'text', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ModerationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationResult
        fields = ['flagged', 'categories', 'category_scores', 'is_spam', 
                 'spam_probability', 'non_spam_probability', 'created_at']


class AIServiceErrorSerializer(serializers.ModelSerializer):
    service_display = serializers.CharField(source='get_service_display', read_only=True)
    input_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = AIServiceError
        fields = ['id', 'service', 'service_display', 'input_text', 'input_preview', 
                 'error_message', 'status_code', 'timestamp']
    
    def get_input_preview(self, obj):
        """Return a truncated preview of the input text for list views"""
        return obj.input_text[:100] + "..." if len(obj.input_text) > 100 else obj.input_text


class AdminReviewWithModerationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    moderation_result = ModerationResultSerializer(read_only=True)
    is_flagged = serializers.SerializerMethodField()
    flagged_categories = serializers.SerializerMethodField()
    is_spam = serializers.SerializerMethodField()
    spam_confidence = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'text', 'created_at', 'moderation_result', 
                 'is_flagged', 'flagged_categories', 'is_spam', 'spam_confidence']
    
    def get_is_flagged(self, obj):
        """Return whether the review is flagged by moderation"""
        return obj.moderation_result.flagged if hasattr(obj, 'moderation_result') else False
    
    def get_flagged_categories(self, obj):
        """Return list of flagged categories"""
        if hasattr(obj, 'moderation_result') and obj.moderation_result.flagged:
            categories = obj.moderation_result.categories
            return [cat for cat, flagged in categories.items() if flagged]
        return []
    
    def get_is_spam(self, obj):
        """Return whether the review is detected as spam"""
        return obj.moderation_result.is_spam if hasattr(obj, 'moderation_result') else False
    
    def get_spam_confidence(self, obj):
        """Return spam detection confidence score"""
        return obj.moderation_result.spam_probability if hasattr(obj, 'moderation_result') else 0.0