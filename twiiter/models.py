from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.CharField(max_length=255, blank=True, default='https://via.placeholder.com/150')

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_absolute_url(self):
        return reverse('twiiter:profile', kwargs={'username': self.user.username})


class Tweet(models.Model):
    content = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tweets')
    image_url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}..."

    class Meta:
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('twiiter:tweet_detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} on {self.tweet}: {self.content[:30]}..."

    class Meta:
        ordering = ['-created_at']


class Like(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tweet', 'user')

    def __str__(self):
        return f"{self.user.username} likes {self.tweet}"


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    tweets = models.ManyToManyField(Tweet, related_name='hashtags')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"#{self.name}"

    def get_absolute_url(self):
        return reverse('twiiter:hashtag', kwargs={'name': self.name})


# Signal to create user profile automatically when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class FavoriteTag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_tags')
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'hashtag')

    def __str__(self):
        return f"{self.user.username} - #{self.hashtag.name}"