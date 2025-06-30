from django.urls import path
from .views import (RegisterView, LoginView, UserListView, UserDeleteView, ReviewListView,
                    AdminReviewsWithModerationView, ReviewDetailView, AIServiceErrorListView,
                    AIServiceErrorDetailView)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('admin/users/', UserListView.as_view(), name='user-list'),
    path('admin/users/<int:user_id>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('reviews/', ReviewListView.as_view(), name='reviews'),
    path('reviews/<int:review_id>/', ReviewDetailView.as_view(), name='review-detail'),
    path('admin/reviews/', AdminReviewsWithModerationView.as_view(), name='admin-reviews-moderation'),
    path('admin/errors/', AIServiceErrorListView.as_view(), name='admin-ai-errors'),
    path('admin/errors/<int:error_id>/', AIServiceErrorDetailView.as_view(), name='admin-ai-error-detail'),
]
