from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .serializers import (RegisterSerializer, LoginSerializer, ReviewSerializer, 
                         ReviewCreateSerializer, AdminReviewWithModerationSerializer)
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsSuperUser
from django.contrib.auth.models import User
from reviews.models import Review, ModerationResult
from rest_framework.permissions import IsAuthenticated
from .tasks import moderate_review_task
from django.db import models


class UserListView(APIView):
    """
    Admin-only endpoint to get all users
    """
    permission_classes = [IsSuperUser]
    
    @extend_schema(
        operation_id="get_all_users",
        description="Get all users (Admin only)",
        responses={200: "List of all users"},
        tags=["Admin"]
    )
    def get(self, request):
        users = User.objects.all().values('id', 'username', 'email', 'is_superuser', 'date_joined')
        return Response(users)


class UserDeleteView(APIView):
    """
    Admin-only endpoint to delete a user
    """
    permission_classes = [IsSuperUser]
    
    @extend_schema(
        operation_id="delete_user",
        description="Delete a user (Admin only)",
        responses={
            200: "User deleted successfully",
            404: "User not found"
        },
        tags=["Admin"]
    )
    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({'detail': 'User deleted successfully'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class RegisterView(APIView):
    """
    Public endpoint for user registration
    """
    permission_classes = []  
    
    @extend_schema(
        operation_id="register_user",
        request=RegisterSerializer,
        description="Register a new user",
        responses={
            201: "User created successfully with token",
            400: "Validation errors"
        },
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Public endpoint for user login
    """
    permission_classes = [] 
    
    @extend_schema(
        operation_id="login_user",
        request=LoginSerializer,
        description="Login with username and password",
        responses={
            200: "Login successful with token",
            400: "Invalid credentials"
        },
        tags=["Authentication"]
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class ReviewListView(APIView):
    """
    Endpoint to get reviews (GET) and create new reviews (POST)
    - Regular users see all reviews except flagged ones
    - Admin users see all reviews (including flagged ones)
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        operation_id="get_reviews",
        description="Get reviews (all non-flagged reviews for users, all reviews for admins)",
        responses={200: ReviewSerializer(many=True)},
        tags=["Reviews"]
    )
    def get(self, request):
        if request.user.is_superuser:
            reviews = Review.objects.all()
        else:
            reviews = Review.objects.filter(
                models.Q(moderation_result__flagged=False) | 
                models.Q(moderation_result__isnull=True)
            )
        
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        operation_id="create_review",
        request=ReviewCreateSerializer,
        description="Create a new review",
        responses={201: ReviewCreateSerializer},
        tags=["Reviews"]
    )
    def post(self, request):
        serializer = ReviewCreateSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(user=request.user)  
            moderate_review_task.delay(review.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailView(generics.RetrieveAPIView):
    """
    Authenticated endpoint to get a specific review by ID with moderation data
    - Requires authentication
    - Shows moderation data if available
    """
    queryset = Review.objects.select_related('moderation_result').all()
    serializer_class = AdminReviewWithModerationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'review_id'

    @extend_schema(
        operation_id="get_review_by_id",
        description="Get a single review by ID, including moderation result if available",
        responses={200: AdminReviewWithModerationSerializer},
        tags=["Reviews"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(
    operation_id="admin_get_reviews_with_moderation",
    description="Get reviews with moderation data (Admin only). Use ?flagged=true for flagged reviews only.",
    parameters=[
        OpenApiParameter(
            name='flagged',
            description='Filter by flagged status',
            required=False,
            type=OpenApiTypes.STR,
            enum=['true', 'false'],
        ),
    ],
    responses={200: AdminReviewWithModerationSerializer(many=True)},
    tags=["Moderation"]
)
class AdminReviewsWithModerationView(generics.ListAPIView):
    """
    Admin-only endpoint to get reviews with their moderation data
    Optional query parameters:
    - ?flagged=true - show only flagged reviews
    - ?flagged=false - show only non-flagged reviews
    """
    serializer_class = AdminReviewWithModerationSerializer
    permission_classes = [IsSuperUser]
    
    def get_queryset(self):
        queryset = Review.objects.select_related('moderation_result').all()
        
        flagged = self.request.query_params.get('flagged', None)
        if flagged is not None:
            if flagged.lower() == 'true':
                queryset = queryset.filter(moderation_result__flagged=True)
            elif flagged.lower() == 'false':
                queryset = queryset.filter(
                    models.Q(moderation_result__flagged=False) | 
                    models.Q(moderation_result__isnull=True)
                )
        
        return queryset