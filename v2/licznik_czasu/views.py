from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Client, Employee, Task, TaskTimer
from .forms import UserForm, ProjectForm, TaskForm, TaskEmployeeForm
from django import forms
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


@login_required()
def view_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task_name = form.cleaned_data['task_name']
            description = form.cleaned_data['description']
            task = Task.objects.create(task_name=task_name, description=description, project_id=project_id)
            return redirect('view_project', project_id)
    else:
        form = TaskForm()

    context = {
        "project": project,
        "form": form,
        "tasks": Task.objects.filter(project_id=project_id)
    }
    return render(request, "licznik_czasu/view_project.html", context)


@login_required()
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

    context = {
        'form': form
    }
    return render(request, "licznik_czasu/create_project.html", context)


@login_required()
def view_task(request, project_id, task_id):
    task = get_object_or_404(Task, pk=task_id)
    project = get_object_or_404(Project, pk=project_id)
    TaskEmployeeForm.base_fields['employee'] = forms.ModelMultipleChoiceField(
        queryset=project.employee, widget=forms.CheckboxSelectMultiple())
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'start':
            start_time = timezone.now()
            request.session['start_time'] = start_time.timestamp()
            request.session['task_id'] = task_id
            timer = TaskTimer.objects.create(task_id=task_id)
            request.session['pk'] = timer.pk
            return JsonResponse({'success': True})
        elif action == 'stop':
            start_time = timezone.datetime.fromtimestamp(float(request.session.get('start_time')))
            end_time = timezone.datetime.fromtimestamp(float(timezone.now().timestamp()))
            duration = end_time - start_time
            # Filter TaskTimer via pk to find the right one
            timer = TaskTimer.objects.get(pk=request.session.get('pk'))
            timer.time_ended = end_time
            timer.time_elapsed = duration
            timer.save()
            request.session['start_time'] = None
            return JsonResponse({'success': True})

        else:
            form = TaskForm(request.POST, instance=task)
            form2 = TaskEmployeeForm(request.POST, instance=task)
            if all([form.is_valid(), form2.is_valid()]):
                form.save()
                form2.save()
                return redirect('view_task', project_id, task_id)
    else:
        form = TaskForm(instance=task)
        form2 = TaskEmployeeForm(instance=task)

    context = {
        "form": form,
        "form2": form2,
        "task": task,
        "project_id": project_id,
        "session_id": request.session.get('task_id'),
        "task_id": task_id,
        'current': request.session.get('start_time')
    }
    return render(request, "licznik_czasu/view_task.html", context)
