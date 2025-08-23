from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('play/<str:difficulty>/', views.play, name='play'),
    path('result/<str:difficulty>/', views.result, name='result'),
]