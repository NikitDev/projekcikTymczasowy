from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect

from .models import Project

# Create your views here.


def posts(request):
    return render(request, 'posts.html')


def home(request):
    projects = Project.objects.all()
    context = {'projects': projects}
    return render(request, 'licznik_czasu/home.html', context)


def view_profile(request):
    args = {'user': request.user}
    return render(request, "account/profile.html", args)


def edit_profile(request):
    args = {'user': request.user}
    return render(request, "account/profile_edit.html", args)


def create_project(request):
    return render(request, "licznik_czasu/create_project.html")


def view_project(request, project_id):
    context = {
        "project": Project.objects.get(pk=project_id)
    }
    return render(request, "licznik_czasu/view_project.html", context)
