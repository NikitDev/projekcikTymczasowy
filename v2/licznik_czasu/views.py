from django.shortcuts import render, redirect
from .models import Project, Client, Employee, Task, TaskTimer
from .forms import UserForm, ProjectForm, TaskForm
from django.utils import timezone
from django.http import JsonResponse


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
    project = Project.objects.get(pk=project_id)
    form = TaskForm()
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task_name = form.cleaned_data['task_name']
            description = form.cleaned_data['description']
            task = Task.objects.create(task_name=task_name, description=description, project_id=project)
            return redirect('view_project', project_id)
    context = {
        "project": Project.objects.get(pk=project_id),
        "form": form,
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


def timer(request, task_id, pk):
    if request.method == 'POST':
        action = request.POST.get('action')  # Get the value of the action attribute to be able to determine whether we are starting or pausing the timer
        if action == 'start':
            start_time = timezone.now()  # Get the
            request.session['start_time'] = start_time.timestamp()  # Keep the start time in the session for easy access later
            timer = TaskTimer.objects.create(task_id=task_id)  # New TaskTimer object with task id
            request.session['pk'] = timer.pk
            return JsonResponse({'success': True})  # Response to js
        elif action == 'stop':
            start_time = timezone.datetime.fromtimestamp(float(request.session.get('start_time')))  # Get start_time from session
            end_time = timezone.now()  # end_time
            duration = end_time - start_time  # Time elapsed between start_time and end_time
            timer = TaskTimer.objects.filter(pk=request.session.get('pk'))  # Filter TaskTimer via pk to find the right one
            timer.time_ended = end_time  # Set end_time to timer
            timer.time_elapsed = duration  # Set duration to timer
            timer.save()  # Save timer
            return JsonResponse({'success': True})  # Response to js
    return render(request, 'timer.html')
