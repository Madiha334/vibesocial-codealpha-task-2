
from django.contrib import admin
from django.urls import path
from social import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.feed_view, name='feed'),
    path('post/create/', views.create_post_view, name='create_post'),
    path('post/<int:post_id>/like/', views.toggle_like_view, name='toggle_like'),
    path('post/<int:post_id>/comment/', views.add_comment_view, name='add_comment'),
    path('post/<int:post_id>/delete/', views.delete_post_view, name='delete_post'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile_view, name='update_profile'),
    path('follow/<str:username>/', views.toggle_follow_view, name='toggle_follow'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]