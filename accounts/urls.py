from django.urls import path
from .views import register, user_logout, edit_profile
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('register/', register, name='register'),
    path("login/", auth_views.LoginView.as_view(redirect_authenticated_user=True), name="login"),
    path("logout/", user_logout, name="logout"),
    path('edit/', edit_profile, name='edit_profile'),

]