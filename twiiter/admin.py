from django.contrib import admin
from .models import Tweet, UserProfile, Comment, Like, Follow, Hashtag, FavoriteTag

@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'birth_date')
    search_fields = ('user__username', 'location')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'tweet', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'tweet', 'created_at')
    list_filter = ('created_at',)

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')

@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(FavoriteTag)
class FavoriteTagAdmin(admin.ModelAdmin):
    list_display = ('user', 'hashtag', 'created_at')
    list_filter = ('user', 'hashtag')
    search_fields = ('user__username', 'hashtag__name')