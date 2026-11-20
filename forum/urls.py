from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.forum_list, name='list'),
    path('create/', views.create_post, name='create'),
    path('<int:pk>/', views.post_detail, name='detail'),
    path('<int:pk>/like/', views.like_post, name='like_post'),
    path('comment/<int:pk>/like/', views.like_comment, name='like_comment'),
    path('user/<int:user_id>/info/', views.user_info, name='user_info'),
]