#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emojimind.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.http import HttpRequest
from django.contrib.sites.shortcuts import get_current_site
from allauth.socialaccount.providers.google.provider import GoogleProvider

print("=== Current Configuration ===")
print("All Sites:", [(s.id, s.domain, s.name) for s in Site.objects.all()])
print("All SocialApp entries:")
for app in SocialApp.objects.all():
    print(f"  ID: {app.id}, Provider: {app.provider}, Name: {app.name}, Sites: {list(app.sites.all())}")

print("\nGoogle Apps specifically:")
google_apps = SocialApp.objects.filter(provider='google')
for app in google_apps:
    print(f"  ID: {app.id}, Name: {app.name}, Client ID: {app.client_id}, Sites: {list(app.sites.all())}")

print("\n=== Testing get_app method ===")
request = HttpRequest()
request.META['HTTP_HOST'] = '127.0.0.1:8000'
site = get_current_site(request)
print("Current site from request:", site)

# Test what the actual error is by simulating the get_app call
try:
    from allauth.socialaccount.providers.google.provider import GoogleProvider
    from allauth.socialaccount.models import SocialApp
    
    # This simulates what get_app does
    current_site = get_current_site(request)
    apps = SocialApp.objects.filter(provider='google', sites=current_site)
    print("Apps matching current site:", apps.count())
    
    if apps.count() > 1:
        print("Multiple apps found - this causes the error!")
        for i, app in enumerate(apps):
            print(f"  App {i+1}: {app.name} (ID: {app.id}, Client ID: {app.client_id})")
    elif apps.count() == 1:
        app = apps.get()
        print("Single app found:", app.name)
    else:
        print("No apps found for current site")
        
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()

# Let's also check what the adapter.py get_app method is doing
print("\n=== Checking SocialApp query directly ===")
try:
    from allauth.socialaccount import app_settings
    from django.contrib.sites.models import Site
    current_site = Site.objects.get_current()
    print("Current site (get_current):", current_site)
    
    # This is what the get_app method does internally
    apps = SocialApp.objects.filter(provider='google', sites=current_site)
    print("Apps found for current site:", apps.count())
    for app in apps:
        print(f"  App: {app.name} (ID: {app.id})")
        
    # Check if there are any apps without site association
    apps_no_site = SocialApp.objects.filter(provider='google', sites=None)
    print("Apps with no site association:", apps_no_site.count())
    
except Exception as e:
    print("Error in direct query:", e)
    import traceback
    traceback.print_exc()
