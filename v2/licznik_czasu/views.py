from django.shortcuts import render, redirect
from .models import Project, Client, Employee, Task
from .forms import UserForm, ProjectForm


# Create your views here.


def posts(request):
    return render(request, 'posts.html')


def home(request):
    projects = Project.objects.all().order_by('id')
    context = {'projects': projects}
    return render(request, 'licznik_czasu/home.html', context)


def view_profile(request):
    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('view_profile')
    else:
        form = UserForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'account/profile.html', context)


def view_project(request, project_id):
    context = {
        "project": Project.objects.get(pk=project_id),
        "tasks": Task.objects.filter(project_id=project_id)
    }
    return render(request, "licznik_czasu/view_project.html", context)


def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project_name = form.cleaned_data['project_name']
            project_description = form.cleaned_data['description']
            project = Project.objects.create(project_name=project_name, description=project_description)
            return redirect('home')
    else:
        form = ProjectForm()
    return render(request, "licznik_czasu/create_project.html", {'form': form})


def edit_project(request, project_id):
    project = Project.objects.get(pk=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('view_project', project_id)
    else:
        form = ProjectForm(instance=project)
    context = {
        'form': form,
        'project': project
    }
    return render(request, "licznik_czasu/edit_project.html", context)
