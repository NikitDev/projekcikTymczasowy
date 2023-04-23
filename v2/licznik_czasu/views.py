from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.views.generic import TemplateView
from .models import Project, Client, Employee, Task, TaskTimer
from .forms import UserForm, ProjectForm, TaskForm
from xhtml2pdf import pisa
from datetime import datetime, timedelta



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


def project_report(request):
    if request.user.who_is != 'CL':
        return HttpResponse('You are not authorized to access this page.')

    projects = Project.objects.filter(client__user=request.user)

    last_day = datetime.now() - timedelta(days=1)
    last_week = datetime.now() - timedelta(weeks=1)
    last_month = datetime.now() - timedelta(weeks=4)

    time_filters = {
        'Last day': last_day,
        'Last week': last_week,
        'Last month': last_month
    }

    context = {
        'projects': projects,
        'time_filters': time_filters,
    }

    if request.method == 'POST':
        selected_project_id = request.POST.get('project', None)
        selected_time_filter = request.POST.get('time_filter', None)

        if selected_project_id is not None:
            selected_project = Project.objects.get(id=selected_project_id)

            if selected_time_filter is not None:
                selected_time_filter_date = time_filters[selected_time_filter]
                tasks = Task.objects.filter(project=selected_project)
                tasktimers = []
                for task in tasks:
                    task_time = list(TaskTimer.objects.filter(task=task))
                    for time in task_time:
                        if time.time_started.date() >= selected_time_filter_date.date():
                            taskinfo = {
                                'name': time.task.task_name,
                                'time_started': time.time_started,
                                'time_elapsed': time.time_elapsed
                            }
                            tasktimers.append(taskinfo)
                print(tasktimers)

        else:
            tasks = None

        if tasks is not None:
            context = {
                'projects': projects,
                'time_filters': time_filters,
                'project': selected_project,
                'tasks': tasks,
                'tasktimer': tasktimers,
                'time_filter': selected_time_filter
            }

    return render(request, 'licznik_czasu/project_report.html', context)

