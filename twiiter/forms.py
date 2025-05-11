from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Tweet, Comment, UserProfile


class TweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ['content', 'image_url']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': "What's happening?", 'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'Image URL (optional)', 'class': 'form-control'})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add a comment...', 'class': 'form-control'})
        }


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'birth_date', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'profile_picture': forms.URLInput(attrs={'class': 'form-control'})
        }


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Search tweets, users, hashtags...', 'class': 'form-control'})
    )