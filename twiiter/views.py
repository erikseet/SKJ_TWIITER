from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import models
from .models import Tweet, UserProfile, Comment, Like, Follow, Hashtag, FavoriteTag
from .forms import TweetForm, CommentForm, UserRegisterForm, UserProfileForm, UserUpdateForm, SearchForm
import re


def home(request):
    if request.user.is_authenticated:
        following_users = User.objects.filter(followers__follower=request.user)
        tweets = Tweet.objects.filter(author__in=list(following_users) + [request.user])
    else:
        tweets = Tweet.objects.all()

    trending_hashtags = Hashtag.objects.annotate(
        tweet_count=models.Count('tweets')
    ).filter(
        tweet_count__gt=0
    ).order_by('-tweet_count')[:5]

    user_liked_tweets = []
    if request.user.is_authenticated:
        user_liked_tweets = Like.objects.filter(user=request.user).values_list('tweet_id', flat=True)

    form = TweetForm()
    if request.method == 'POST' and request.user.is_authenticated:
        form = TweetForm(request.POST)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.author = request.user
            tweet.save()

            hashtag_pattern = re.compile(r'#(\w+)')
            hashtags = hashtag_pattern.findall(tweet.content)

            for tag in hashtags:
                hashtag, created = Hashtag.objects.get_or_create(name=tag.lower())
                hashtag.tweets.add(tweet)

            messages.success(request, 'Your tweet has been posted!')
            return redirect('twiiter:home')

    return render(request, 'twiiter/home.html', {
        'tweets': tweets,
        'form': form,
        'trending_hashtags': trending_hashtags,
        'user_liked_tweets': user_liked_tweets
    })

def tweet_detail(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    comments = tweet.comments.all()

    user_liked = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(tweet=tweet, user=request.user).exists()

    comment_form = CommentForm()
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.tweet = tweet
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('twiiter:tweet_detail', pk=pk)

    context = {
        'tweet': tweet,
        'comments': comments,
        'comment_form': comment_form,
        'user_liked': user_liked,
        'likes_count': tweet.likes.count(),
    }
    return render(request, 'twiiter/tweet_detail.html', context)


@login_required
def create_tweet(request):
    if request.method == 'POST':
        form = TweetForm(request.POST)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.author = request.user
            tweet.save()

            hashtag_pattern = re.compile(r'#(\w+)')
            hashtags = hashtag_pattern.findall(tweet.content)

            for tag in hashtags:
                hashtag, created = Hashtag.objects.get_or_create(name=tag.lower())
                hashtag.tweets.add(tweet)

            messages.success(request, 'Your tweet has been posted!')
            return redirect('twiiter:home')
    else:
        form = TweetForm()

    return render(request, 'twiiter/create_tweet.html', {'form': form})


@login_required
def edit_tweet(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)

    if tweet.author != request.user:
        messages.error(request, "You cannot edit someone else's tweet!")
        return redirect('twiiter:tweet_detail', pk=pk)

    if request.method == 'POST':
        form = TweetForm(request.POST, instance=tweet)
        if form.is_valid():
            updated_tweet = form.save()

            updated_tweet.hashtags.clear()
            hashtag_pattern = re.compile(r'#(\w+)')
            hashtags = hashtag_pattern.findall(updated_tweet.content)

            for tag in hashtags:
                hashtag, created = Hashtag.objects.get_or_create(name=tag.lower())
                hashtag.tweets.add(updated_tweet)

            messages.success(request, 'Your tweet has been updated!')
            return redirect('twiiter:tweet_detail', pk=pk)
    else:
        form = TweetForm(instance=tweet)

    return render(request, 'twiiter/edit_tweet.html', {'form': form, 'tweet': tweet})


@login_required
def delete_tweet(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)

    if tweet.author != request.user:
        messages.error(request, "You cannot delete someone else's tweet!")
        return redirect('twiiter:tweet_detail', pk=pk)

    if request.method == 'POST':
        tweet.delete()
        messages.success(request, 'Your tweet has been deleted!')
        return redirect('twiiter:home')

    return render(request, 'twiiter/delete_tweet.html', {'tweet': tweet})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    tweets = user.tweets.all()

    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()

    context = {
        'profile_user': user,
        'tweets': tweets,
        'is_following': is_following,
        'followers_count': user.followers.count(),
        'following_count': user.following.count(),
    }
    return render(request, 'twiiter/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('twiiter:profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'twiiter/edit_profile.html', context)


@login_required
def follow_toggle(request, username):
    user_to_toggle = get_object_or_404(User, username=username)

    if request.user == user_to_toggle:
        messages.error(request, "You cannot follow yourself!")
        return redirect('twiiter:profile', username=username)

    follow_relation, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_toggle
    )

    if not created:
        follow_relation.delete()
        messages.success(request, f"You unfollowed {username}")
    else:
        messages.success(request, f"You are now following {username}")

    return redirect('twiiter:profile', username=username)


@login_required
def like_toggle(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)

    like, created = Like.objects.get_or_create(user=request.user, tweet=tweet)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    # AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'likes_count': tweet.likes.count()
        })

    # For non-AJAX request
    return redirect('twiiter:tweet_detail', pk=pk)


def search(request):
    form = SearchForm()
    results = {'tweets': [], 'users': [], 'hashtags': []}

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            # Search tweets
            results['tweets'] = Tweet.objects.filter(content__icontains=query)

            # Search users
            results['users'] = User.objects.filter(username__icontains=query)

            # Search hashtags
            results['hashtags'] = Hashtag.objects.filter(name__icontains=query)

    return render(request, 'twiiter/search.html', {'form': form, 'results': results})


def hashtag(request, name):
    hashtag = get_object_or_404(Hashtag, name=name)
    tweets = hashtag.tweets.all()

    related_hashtags = Hashtag.objects.filter(
        tweets__in=tweets
    ).exclude(
        name=name
    ).annotate(
        common_count=models.Count('id')
    ).order_by('-common_count')[:5]

    return render(request, 'twiiter/hashtag.html', {
        'hashtag': hashtag,
        'tweets': tweets,
        'related_hashtags': related_hashtags
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('twiiter:home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('twiiter:login')
    else:
        form = UserRegisterForm()

    return render(request, 'twiiter/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('twiiter:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('twiiter:home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'twiiter/login.html')


# API views for REST API
def api_tweets(request):
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
    user = get_object_or_404(User, username=username)

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


def followers_list(request, username):
    user = get_object_or_404(User, username=username)
    followers = User.objects.filter(following__following=user)

    return render(request, 'twiiter/user_list.html', {
        'users': followers,
        'title': f"People following {username}",
        'profile_user': user
    })


def following_list(request, username):
    user = get_object_or_404(User, username=username)
    following = User.objects.filter(followers__follower=user)

    return render(request, 'twiiter/user_list.html', {
        'users': following,
        'title': f"People {username} follows",
        'profile_user': user
    })


def for_you(request):
    popular_tweets = Tweet.objects.annotate(
        likes_count=models.Count('likes')
    ).order_by('-likes_count')[:10]

    recommended_tweets = []
    if request.user.is_authenticated:
        favorite_hashtags = Hashtag.objects.filter(
            favoritetag__user=request.user
        )

        if favorite_hashtags.exists():
            recommended_tweets = Tweet.objects.filter(
                hashtags__in=favorite_hashtags
            ).exclude(
                id__in=[t.id for t in popular_tweets]
            ).distinct().order_by('-created_at')[:10]

        if not recommended_tweets:
            recommended_tweets = Tweet.objects.exclude(
                id__in=[t.id for t in popular_tweets]
            ).order_by('?')[:10]

    user_liked_tweets = []
    if request.user.is_authenticated:
        user_liked_tweets = Like.objects.filter(user=request.user).values_list('tweet_id', flat=True)

    return render(request, 'twiiter/for_you.html', {
        'popular_tweets': popular_tweets,
        'recommended_tweets': recommended_tweets,
        'user_liked_tweets': user_liked_tweets
    })


@login_required
def favorite_tags(request, username):
    user = get_object_or_404(User, username=username)

    if request.user != user:
        messages.error(request, "You can only view your own favorite tags!")
        return redirect('twiiter:profile', username=username)

    favorite_tags = FavoriteTag.objects.filter(user=user).select_related('hashtag')
    all_hashtags = Hashtag.objects.all().order_by('name')

    return render(request, 'twiiter/favorite_tags.html', {
        'favorite_tags': favorite_tags,
        'all_hashtags': all_hashtags
    })


@login_required
def add_custom_favorite_tag(request):
    if request.method == 'POST':
        hashtag_name = request.POST.get('hashtag_name', '').strip().lower()

        if not hashtag_name:
            messages.error(request, "Hashtag name cannot be empty.")
            return redirect('twiiter:favorite_tags', username=request.user.username)

        if hashtag_name.startswith('#'):
            hashtag_name = hashtag_name[1:]

        try:
            hashtag, created = Hashtag.objects.get_or_create(name=hashtag_name)

            favorite, created_fav = FavoriteTag.objects.get_or_create(
                user=request.user,
                hashtag=hashtag
            )

            if created_fav:
                messages.success(request, f"Added #{hashtag_name} to your favorites!")
            else:
                messages.info(request, f"#{hashtag_name} is already in your favorites.")

        except Exception as e:
            print(f"Error adding custom hashtag: {e}")
            messages.error(request, f"Error adding hashtag: {str(e)}")

    return redirect('twiiter:favorite_tags', username=request.user.username)
@login_required
def add_favorite_tag(request, hashtag_id):
    hashtag = get_object_or_404(Hashtag, id=hashtag_id)

    favorite, created = FavoriteTag.objects.get_or_create(
        user=request.user,
        hashtag=hashtag
    )

    if created:
        messages.success(request, f"Added #{hashtag.name} to your favorites!")
    else:
        messages.info(request, f"#{hashtag.name} is already in your favorites.")

    next_page = request.META.get('HTTP_REFERER',
                                 reverse('twiiter:favorite_tags',
                                         kwargs={'username': request.user.username}))
    return redirect(next_page)


@login_required
def remove_favorite_tag(request, hashtag_id):
    hashtag = get_object_or_404(Hashtag, id=hashtag_id)

    try:
        favorite = FavoriteTag.objects.get(user=request.user, hashtag=hashtag)
        favorite.delete()
        messages.success(request, f"Removed #{hashtag.name} from your favorites.")
    except FavoriteTag.DoesNotExist:
        messages.error(request, f"#{hashtag.name} is not in your favorites.")

    next_page = request.META.get('HTTP_REFERER',
                                 reverse('twiiter:favorite_tags',
                                         kwargs={'username': request.user.username}))
    return redirect(next_page)


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        messages.error(request, "You cannot edit someone else's comment!")
        return redirect('twiiter:tweet_detail', pk=comment.tweet.id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your comment has been updated!')
            return redirect('twiiter:tweet_detail', pk=comment.tweet.id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'twiiter/edit_comment.html', {
        'form': form,
        'comment': comment
    })


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        messages.error(request, "You cannot delete someone else's comment!")
        return redirect('twiiter:tweet_detail', pk=comment.tweet.id)

    if request.method == 'POST':
        tweet_id = comment.tweet.id
        comment.delete()
        messages.success(request, 'Your comment has been deleted!')
        return redirect('twiiter:tweet_detail', pk=tweet_id)

    return render(request, 'twiiter/delete_comment.html', {'comment': comment})