from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view),
    path('register/', views.register_view),
    path('logout/', views.logout_view),
    path('profile/', views.profile_view),
    path('add-post/', views.add_post_view),
    path('like/<int:post_id>/', views.like_post_view),
    path('comment/<int:post_id>/', views.add_comment_view),
]
