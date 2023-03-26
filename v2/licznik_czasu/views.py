from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from .models import Project, Client, Employee
from .forms import UserForm


# Create your views here.


def posts(request):
    return render(request, 'posts.html')


def home(request):
    projects = Project.objects.all()
    context = {'projects': projects}
    return render(request, 'licznik_czasu/home.html', context)


def view_profile(request):
    user = request.user

    try:
        client = Client.objects.get(user=user)
        phone_number = client.phone_number
    except Client.DoesNotExist:
        try:
            employee = Employee.objects.get(user=user)
            phone_number = employee.phone_number
        except Employee.DoesNotExist:
            phone_number = "Brak numeru telefonu"

    context = {
        'user': user,
        'phone_number': phone_number
    }
    return render(request, 'account/profile.html', context)


def edit_profile(request):
    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('view_profile')
    else:
        form = UserForm(instance=request.user)
    return render(request, 'account/profile_edit.html', {'form': form})


def create_project(request):
    return render(request, "licznik_czasu/create_project.html")


def view_project(request, project_id):
    context = {
        "project": Project.objects.get(pk=project_id)
    }
    return render(request, "licznik_czasu/view_project.html", context)
