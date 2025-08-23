from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from django.urls import reverse

class NoSignupAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # Allow signup - the template will handle showing only Google OAuth
        return True
    
    def respond_user_inactive(self, request, user):
        # Redirect inactive users to Google login
        return redirect('account_login')
    
    def get_login_redirect_url(self, request):
        # Always redirect to home after login
        return '/'
    
    def save_user(self, request, user, form, commit=True):
        # Block manual form-based signup by redirecting to Google
        return redirect('account_login')

class GoogleOnlySocialAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        # Always allow social signup through Google
        return True