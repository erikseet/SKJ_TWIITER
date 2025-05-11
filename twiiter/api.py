from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Tweet, UserProfile, Comment, Like, Follow, Hashtag


def api_tweets(request):
    """API endpoint to get all tweets"""
    tweets = Tweet.objects.all()
    data = []

    for tweet in tweets:
        data.append({
            'id': tweet.id,
            'content': tweet.content,
            'author': tweet.author.username,
            'created_at': tweet.created_at.isoformat(),
            'likes_count': tweet.likes.count(),
            'comments_count': tweet.comments.count(),
        })

    return JsonResponse({'tweets': data})


def api_tweet_detail(request, pk):
    """API endpoint to get a specific tweet with its comments"""
    tweet = get_object_or_404(Tweet, pk=pk)
    comments = []

    for comment in tweet.comments.all():
        comments.append({
            'id': comment.id,
            'content': comment.content,
            'author': comment.author.username,
            'created_at': comment.created_at.isoformat(),
        })

    data = {
        'id': tweet.id,
        'content': tweet.content,
        'author': tweet.author.username,
        'created_at': tweet.created_at.isoformat(),
        'likes_count': tweet.likes.count(),
        'comments': comments,
    }

    return JsonResponse(data)


def api_user_profile(request, username):
    """API endpoint to get a user's profile and recent tweets"""
    user = get_object_or_404(User, username=username)

    # Recent tweets
    tweets = []
    for tweet in user.tweets.all()[:5]:
        tweets.append({
            'id': tweet.id,
            'content': tweet.content,
            'created_at': tweet.created_at.isoformat(),
            'likes_count': tweet.likes.count(),
        })

    data = {
        'username': user.username,
        'name': f"{user.first_name} {user.last_name}".strip(),
        'bio': user.profile.bio,
        'location': user.profile.location,
        'followers_count': user.followers.count(),
        'following_count': user.following.count(),
        'recent_tweets': tweets,
    }

    return JsonResponse(data)


def api_hashtags(request):
    """API endpoint to get trending hashtags"""
    hashtags = Hashtag.objects.all().order_by('-created_at')
    data = []

    for hashtag in hashtags:
        data.append({
            'name': hashtag.name,
            'tweets_count': hashtag.tweets.count(),
        })

    return JsonResponse({'hashtags': data})


def api_search(request):
    """API endpoint to search tweets, users and hashtags"""
    query = request.GET.get('q', '')

    if not query:
        return JsonResponse({'error': 'No search query provided'}, status=400)

    tweets = Tweet.objects.filter(content__icontains=query)
    users = User.objects.filter(username__icontains=query)
    hashtags = Hashtag.objects.filter(name__icontains=query)

    data = {
        'tweets': [
            {
                'id': tweet.id,
                'content': tweet.content,
                'author': tweet.author.username,
                'created_at': tweet.created_at.isoformat(),
            } for tweet in tweets[:10]
        ],
        'users': [
            {
                'username': user.username,
                'bio': user.profile.bio,
            } for user in users[:10]
        ],
        'hashtags': [
            {
                'name': hashtag.name,
                'tweets_count': hashtag.tweets.count(),
            } for hashtag in hashtags[:10]
        ]
    }

    return JsonResponse(data)