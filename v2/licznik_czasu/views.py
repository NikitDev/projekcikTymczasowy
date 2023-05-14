from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template

from .models import Project, Task, TaskTimer, Client, Employee
from .forms import UserForm, ProjectForm, TaskForm, TaskEmployeeForm
from django import forms
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from xhtml2pdf import pisa
from datetime import datetime, timedelta


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


@login_required
def project_report(request, project_id):
    if request.user.who_is != 'CL':
        return HttpResponse('Nie masz dostepu do tej strony.')

    project = get_object_or_404(Project, pk=project_id)

    last_day = datetime.now() - timedelta(days=1)
    last_week = datetime.now() - timedelta(weeks=1)
    last_month = datetime.now() - timedelta(weeks=4)

    time_filters = {
        'Last day': last_day,
        'Last week': last_week,
        'Last month': last_month
    }

    context = {
        'project': project,
        'time_filters': time_filters
    }

    if request.method == 'POST':
        selected_time_filter = request.POST.get('time_filter', None)
        generate_report = request.POST.get('generate_report', None)
        task_filter = request.POST.get('task_filter', None)

        if selected_time_filter is not None:
            selected_time_filter_date = time_filters[selected_time_filter]
            tasks = Task.objects.filter(project=project_id)

            tasktimers = []
            tasktotal = []

            for task in tasks:
                task_time = list(TaskTimer.objects.filter(task=task))

                total = timedelta(0) # łączny czas na każdego taska.
                tasktimers2=[]

                for time in task_time:
                    if time.time_started.date() >= selected_time_filter_date.date():
                        if time.time_elapsed:
                            total += time.time_elapsed

                        taskinfo = {
                            'name': time.task.task_name,
                            'time_started': time.time_started,
                            'time_ended': time.time_ended,
                            'time_elapsed': time.time_elapsed,
                            'employee': time.user
                        }
                        tasktimers.append(taskinfo)
                        tasktimers2.append(taskinfo)

                task3 = {
                    'task': task,
                    'total_elapsed': total,
                    'all_timers':tasktimers2
                }
                tasktotal.append(task3)
        else:
            tasks = None

        if tasks:
            context = {
                'time_filters': time_filters,
                'project': project,
                'tasks': tasks,
                'tasktimer': tasktimers,
                'time_filter': selected_time_filter,
                'selected_time_filter_date': selected_time_filter_date,
                'tasktotal': tasktotal
            }

        if generate_report is not None:
            template_path = 'licznik_czasu/pdf_template.html'
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="project_report.pdf"'
            template = get_template(template_path)
            html = template.render(context)
            pisa_status = pisa.CreatePDF(html, dest=response)
            if pisa_status.err:
                return HttpResponse('error')
            return response

    return render(request, 'licznik_czasu/project_report.html', context)
