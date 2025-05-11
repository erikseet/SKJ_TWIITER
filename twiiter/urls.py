from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import api

app_name = 'twiiter'

urlpatterns = [
    # Basic views
    path('', views.home, name='home'),
    path('tweet/<int:pk>/', views.tweet_detail, name='tweet_detail'),
    path('tweet/new/', views.create_tweet, name='create_tweet'),
    path('tweet/<int:pk>/edit/', views.edit_tweet, name='edit_tweet'),
    path('tweet/<int:pk>/delete/', views.delete_tweet, name='delete_tweet'),

    path('profile/edit/', views.edit_profile, name='edit_profile'),

    path('profile/<str:username>/', views.profile, name='profile'),

    path('follow/<str:username>/', views.follow_toggle, name='follow_toggle'),
    path('like/<int:pk>/', views.like_toggle, name='like_toggle'),
    path('search/', views.search, name='search'),

    path('hashtag/add-custom-favorite/', views.add_custom_favorite_tag, name='add_custom_favorite_tag'),

    path('hashtag/<str:name>/', views.hashtag, name='hashtag'),

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='twiiter:home'), name='logout'),

    # API endpoints
    path('api/tweets/', api.api_tweets, name='api_tweets'),
    path('api/tweet/<int:pk>/', api.api_tweet_detail, name='api_tweet_detail'),
    path('api/user/<str:username>/', api.api_user_profile, name='api_user_profile'),
    path('api/hashtags/', api.api_hashtags, name='api_hashtags'),
    path('api/search/', api.api_search, name='api_search'),

    path('profile/<str:username>/followers/', views.followers_list, name='followers'),
    path('profile/<str:username>/following/', views.following_list, name='following'),
    path('for-you/', views.for_you, name='for_you'),
    path('profile/<str:username>/favorite-tags/', views.favorite_tags, name='favorite_tags'),
    path('hashtag/<int:hashtag_id>/add-favorite/', views.add_favorite_tag, name='add_favorite_tag'),
    path('hashtag/<int:hashtag_id>/remove-favorite/', views.remove_favorite_tag, name='remove_favorite_tag'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]