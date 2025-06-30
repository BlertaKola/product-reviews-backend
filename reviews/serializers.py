from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from reviews.models import Review, ModerationResult

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


# Admin-only serializers for moderation
class ModerationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationResult
        fields = ['flagged', 'categories', 'category_scores', 'created_at']


class AdminReviewWithModerationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    moderation_result = ModerationResultSerializer(read_only=True)
    is_flagged = serializers.SerializerMethodField()
    flagged_categories = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'text', 'created_at', 'moderation_result', 'is_flagged', 'flagged_categories']
    
    def get_is_flagged(self, obj):
        """Return whether the review is flagged by moderation"""
        return obj.moderation_result.flagged if hasattr(obj, 'moderation_result') else False
    
    def get_flagged_categories(self, obj):
        """Return list of flagged categories"""
        if hasattr(obj, 'moderation_result') and obj.moderation_result.flagged:
            categories = obj.moderation_result.categories
            return [cat for cat, flagged in categories.items() if flagged]
        return []