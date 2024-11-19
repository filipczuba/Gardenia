from django.urls import path
from .views import ReviewablePostsView,LandlordReviewsView,ReviewCreateView, user_reviews,landlord_reviews,edit_review, delete_review

urlpatterns = [
    path('reviewable/', ReviewablePostsView.as_view(), name='reviewable_posts'),
    path('landlord-reviews/', LandlordReviewsView.as_view(), name='landlord_reviews'),
    path('review/create/<int:rent_request_id>/', ReviewCreateView.as_view(), name='review_create'),
    path('my-reviews/', user_reviews, name='user_reviews'),
    path('landlord-reviews/', landlord_reviews, name='landlord_reviews'),
    path('review/edit/<int:pk>/', edit_review, name='edit_review'),
    path('review/delete/<int:pk>/', delete_review, name='delete_review'),
]