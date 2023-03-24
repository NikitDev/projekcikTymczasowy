from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect


# Create your views here.


def posts(request):
    return render(request, 'posts.html')


def home(request):
    return render(request, 'home.html')


def profile(request):
    return render(request, 'profile.html')

