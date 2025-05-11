import os
import django
import random
from datetime import timedelta
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'DjangoProject.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from twiiter.models import Tweet, UserProfile, Follow, Hashtag
from django.db import transaction

# Sample data
USERS = [
    {'username': 'john_doe', 'email': 'john@example.com', 'password': 'testpassword123',
     'bio': 'Just a regular guy trying to tweet.', 'location': 'New York'},
    {'username': 'jane_smith', 'email': 'jane@example.com', 'password': 'testpassword123',
     'bio': 'Digital marketer and coffee lover.', 'location': 'San Francisco'},
    {'username': 'techguru', 'email': 'tech@example.com', 'password': 'testpassword123',
     'bio': 'Sharing the latest in tech and gadgets.', 'location': 'Silicon Valley'},
    {'username': 'foodlover', 'email': 'food@example.com', 'password': 'testpassword123',
     'bio': 'Eating my way through life, one meal at a time.', 'location': 'Chicago'},
    {'username': 'travelbug', 'email': 'travel@example.com', 'password': 'testpassword123',
     'bio': 'Exploring the world, one country at a time.', 'location': 'Everywhere'},
    {'username': 'fitness_freak', 'email': 'fitness@example.com', 'password': 'testpassword123',
     'bio': 'Fitness enthusiast and personal trainer.', 'location': 'Los Angeles'},
    {'username': 'bookworm', 'email': 'books@example.com', 'password': 'testpassword123',
     'bio': 'Reading all the books, sharing all the thoughts.', 'location': 'Boston'},
    {'username': 'music_lover', 'email': 'music@example.com', 'password': 'testpassword123',
     'bio': 'Music is life. Everything else is just details.', 'location': 'Nashville'},
    {'username': 'artsy_soul', 'email': 'art@example.com', 'password': 'testpassword123',
     'bio': 'Finding beauty in everything.', 'location': 'Paris'},
    {'username': 'code_ninja', 'email': 'code@example.com', 'password': 'testpassword123',
     'bio': 'Turning caffeine into code since 2010.', 'location': 'Seattle'}
]

TWEET_CONTENTS = [
    "Just had the most amazing coffee! #coffeelover #morning",
    "Working on a new project today. So excited! #coding #newproject",
    "Beautiful sunset this evening. #nature #views",
    "Can't believe how good the new movie was! #cinema #movienight",
    "Just finished reading an amazing book. Highly recommend! #reading #bookreview",
    "Tried a new recipe today and it turned out great! #cooking #foodie",
    "Monday motivation: Just do it! #motivation #monday",
    "Missing the beach already... #travel #vacation",
    "New workout routine is killing me, but feeling great! #fitness #health",
    "Learning something new every day. #learning #growth",
    "Throwback to last summer's adventures! #tbt #memories",
    "Who else is excited for the weekend? #weekend #friday",
    "Just adopted the cutest puppy! #pets #doglovers",
    "Music makes everything better. #music #playlist",
    "Coding all night. Debugging is fun! #programming #developer",
    "Nature walks are the best therapy. #outdoors #hiking",
    "My garden is finally blooming! #gardening #spring",
    "Sometimes a simple cup of tea solves everything. #tea #relaxation",
    "Discovering new places in my own city. #exploration #citylife",
    "Art is the expression of the soul. #art #creativity",
    "Technology is amazing when it works! #tech #innovation",
    "Finding joy in the little things. #gratitude #happiness",
    "The gym was packed today! #workout #fitness",
    "New favorite podcast discovered! #podcast #listening",
    "Is it just me or is time flying by? #thoughts #time",
    "Remote work has its perks. #wfh #remotework",
    "Finally mastered that recipe I've been working on. #cooking #achievement",
    "Sometimes all you need is a good conversation. #friends #connection",
    "Excited to announce some big news soon! #announcement #staytuned",
    "Just watched the most incredible sunset. Nature is amazing! #sunset #nature"
]

HASHTAGS = [
    "coffeelover", "morning", "coding", "newproject", "nature", "views",
    "cinema", "movienight", "reading", "bookreview", "cooking", "foodie",
    "motivation", "monday", "travel", "vacation", "fitness", "health",
    "learning", "growth", "tbt", "memories", "weekend", "friday",
    "pets", "doglovers", "music", "playlist", "programming", "developer",
    "outdoors", "hiking", "gardening", "spring", "tea", "relaxation",
    "exploration", "citylife", "art", "creativity", "tech", "innovation",
    "gratitude", "happiness", "workout", "podcast", "listening", "thoughts",
    "time", "wfh", "remotework", "achievement", "friends", "connection",
    "announcement", "staytuned", "sunset"
]


@transaction.atomic
def create_users():
    """Create sample users."""
    created_users = []
    for user_data in USERS:
        # Skip if user already exists
        if User.objects.filter(username=user_data['username']).exists():
            print(f"User {user_data['username']} already exists. Skipping.")
            continue

        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']
        )
        # Update profile
        profile = user.profile
        profile.bio = user_data['bio']
        profile.location = user_data['location']
        profile.save()

        created_users.append(user)
        print(f"Created user: {user.username}")

    return created_users


@transaction.atomic
def create_follows(users):
    """Create random follows between users."""
    for follower in users:
        # Each user follows 3-6 random users
        follow_count = random.randint(3, 6)
        potential_followings = [u for u in users if u != follower]
        followings = random.sample(potential_followings, min(follow_count, len(potential_followings)))

        for following in followings:
            Follow.objects.get_or_create(
                follower=follower,
                following=following
            )
            print(f"{follower.username} now follows {following.username}")


@transaction.atomic
def create_tweets(users):
    """Create random tweets with hashtags."""
    created_tweets = []

    for _ in range(30):  # Create 30 tweets
        user = random.choice(users)
        content = random.choice(TWEET_CONTENTS)

        # Create tweet
        tweet = Tweet.objects.create(
            author=user,
            content=content,
            created_at=timezone.now() - timedelta(days=random.randint(0, 14),
                                                  hours=random.randint(0, 23),
                                                  minutes=random.randint(0, 59))
        )
        created_tweets.append(tweet)

        # Extract and create hashtags
        import re
        hashtag_pattern = re.compile(r'#(\w+)')
        hashtags = hashtag_pattern.findall(content)

        for tag in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(name=tag.lower())
            hashtag.tweets.add(tweet)
            action = "Created" if created else "Used existing"
            print(f"{action} hashtag: #{tag}")

        print(f"Created tweet by {user.username}: {content[:30]}...")

    return created_tweets


def run():
    """Run the population script."""
    print("Starting population script...")

    # Create users
    users = User.objects.all()
    if users.count() < 10:  # Only create users if we have fewer than 10
        users = create_users()
    else:
        users = list(users)
        print(f"Using {len(users)} existing users")

    # Create follows between users
    create_follows(users)

    # Create tweets with hashtags
    create_tweets(users)

    print("Population completed successfully!")


if __name__ == '__main__':
    print("Populating the database...")
    run()
    print("Population complete!")