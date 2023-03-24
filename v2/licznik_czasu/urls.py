from django.urls import path

from . import views

urlpatterns = [
    path('posts', views.posts, name='posts'),
    path('', views.home, name='home'),
    path('profile', views.profile, name='profile')
]
