from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Project, Task, TaskTimer, Client, Employee
from .forms import UserForm, ProjectForm, TaskForm, TaskEmployeeForm
from django import forms
from django.utils import timezone
from django.http import JsonResponse

import schedule
import threading
import json
import time


def home(request):
    if request.user.is_anonymous:
        projects = []
    elif request.user.is_superuser:
        projects = Project.objects.all().order_by("id")
    elif request.user.who_is == "CL":
        client_id = Client.objects.get(user_id=request.user.id).id
        projects = Project.objects.filter(client=client_id).order_by('id')
    else:
        employee_id = Employee.objects.get(user_id=request.user.id).id
        projects = Project.objects.filter(employee=employee_id).order_by('id')
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


@login_required
def view_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task_name = request.POST.get('task_name')
            description = request.POST.get('description')
            task = Task.objects.create(task_name=task_name, description=description, project_id=project_id)
            return JsonResponse({"message": "Task added successfully"})
        return JsonResponse({"message": "Form not valid"})
    else:
        form = TaskForm()

    context = {
        "project": project,
        "form": form,
        "tasks": Task.objects.filter(project_id=project_id).order_by('id')
    }
    return render(request, "licznik_czasu/view_project.html", context)


@login_required
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


class SchedulerThread(threading.Thread):
    def __init__(self, start_time_a, timer_id):
        super().__init__()
        self.start_time_a = start_time_a
        self.timer_id = timer_id
        self.stop_scheduler = threading.Event()

    def run(self):
        while not self.stop_scheduler.is_set():
            schedule.run_pending()
            time.sleep(1)
            print("TEST")

    def stop(self):
        print("Stopped")
        self.stop_scheduler.set()


class StopThread:
    def __init__(self, schedule_job, thread):
        self.schedule_job = schedule_job
        self.thread = thread

    def stop(self):
        schedule.cancel_job(self.schedule_job)
        self.thread.stop()
        self.thread.join()


def autosave(request, start_time_a, timer_id):
    timer_a = TaskTimer.objects.get(pk=timer_id, user=request.user)
    print(timer_id, " timer id XD")
    if timer_a:
        now = timezone.datetime.fromtimestamp(float(timezone.now().timestamp()))
        time_el = now - timezone.datetime.fromtimestamp(float(start_time_a))
        timer_a.time_elapsed = time_el
        timer_a.time_ended = now
        timer_a.save()


@login_required
def view_task(request, project_id, task_id):
    task = get_object_or_404(Task, pk=task_id)
    project = get_object_or_404(Project, pk=project_id)
    TaskEmployeeForm.base_fields['employee'] = forms.ModelMultipleChoiceField(
        queryset=project.employee, widget=forms.CheckboxSelectMultiple(), required=False)

    if request.method == 'POST':
        action = request.POST.get('action')
        form = TaskForm(request.POST, instance=task)
        form2 = TaskEmployeeForm(request.POST, instance=task)
        if action == 'start':
            start_time = timezone.now()
            request.session['start_time'] = start_time.timestamp()
            request.session['task_id'] = task_id
            timer = TaskTimer.objects.create(task_id=task_id, user=request.user)
            request.session['pk'] = timer.pk

            schedule.every(5).seconds.do(autosave, request, request.session.get('start_time'), request.session.get('pk')).tag(request.session.get('pk'))

            scheduler_thread = SchedulerThread(request.session.get('start_time'), request.session.get('pk'))
            scheduler_thread.start()

            timer.schedule_thread = scheduler_thread.name
            timer.save()

            return JsonResponse({'success': True})
        elif action == 'stop':
            timer_s = TaskTimer.objects.get(pk=request.session.get('pk'), user=request.user)
            scheduler_thread = timer_s.schedule_thread
            if scheduler_thread is not None:
                for thread in threading.enumerate():
                    if thread.getName() == scheduler_thread:
                        job = schedule.get_jobs(request.session.get('pk'))[0]
                        thr = StopThread(job, thread)
                        thr.stop()
                        break

            start_time = timezone.datetime.fromtimestamp(float(request.session.get('start_time')))
            end_time = timezone.datetime.fromtimestamp(float(timezone.now().timestamp()))
            duration = end_time - start_time
            # Filter TaskTimer via pk to find the right one
            timer = TaskTimer.objects.get(pk=request.session.get('pk'))
            print(request.session.get('pk'), ' To tez timer ID XDDDDDDDDD')
            timer.time_ended = end_time
            timer.time_elapsed = duration
            timer.save()
            request.session['start_time'] = None
            request.session['pk'] = None
            return JsonResponse({'success': True})
        # Handle forms
        elif action == "task-info-form":
            if form.is_valid():
                form.save()
                return JsonResponse({"message": "Task changed successfully"})
            return JsonResponse({"message": "Task change unsuccessfull"})
        elif action == "employee-form":
            if form2.is_valid():
                form2.save()
                return JsonResponse({"message": "Employee/s added successfully"})
            return JsonResponse({"message": "Employee form not valid"})
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
