# posts/urls.py
from django.urls import path
from .views import (
    LandlordPropertiesView, LandlordRentRequestsView, RenterBookingsView,
    PostCreateView, PostUpdateView, PostDeleteView, RentRequestCreateView, RentRequestActionView, PostDetailView
)

urlpatterns = [
    path('landlord/properties/', LandlordPropertiesView.as_view(), name='landlord_properties'),
    path('landlord/rent-requests/', LandlordRentRequestsView.as_view(), name='landlord_rent_requests'),
    path('renter/bookings/', RenterBookingsView.as_view(), name='renter_bookings'),
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('edit/<int:pk>/', PostUpdateView.as_view(), name='post_edit'),
    path('delete/<int:pk>/', PostDeleteView.as_view(), name='post_delete'),
    path('rent-request/<int:post_id>/', RentRequestCreateView.as_view(), name='rent_request_create'),
    path('rent-request/<int:pk>/approve/', 
         RentRequestActionView.as_view(action='approve'), name='approve_rent_request'),
    path('rent-request/<int:pk>/reject/', 
         RentRequestActionView.as_view(action='reject'), name='reject_rent_request'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    
]
