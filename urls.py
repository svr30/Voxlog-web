# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('add_post/', views.add_post_view, name='add_post'),
    path('post/<int:post_id>/add_comment/', views.add_comment_view, name='add_comment'),
    path('post/<int:post_id>/like/', views.like_post_view, name='like_post'), # New URL
]