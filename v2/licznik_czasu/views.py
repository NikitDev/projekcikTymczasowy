from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import get_template

from .models import Project, Task, TaskTimer, Client, Employee
from .forms import UserForm, TaskForm, TaskEmployeeForm
from django import forms
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from xhtml2pdf import pisa
from datetime import datetime, timedelta


def can_access_project(request, project_id):
    if request.user.is_superuser:
        return
    elif request.user.who_is == "CL":
        client_id = Client.objects.get(user_id=request.user.id)
        project = get_object_or_404(Project, pk=project_id)
        if project.client == client_id:
            return
    else:
        employee = Employee.objects.get(user_id=request.user.id)
        project = get_object_or_404(Project, pk=project_id)
        if employee in project.employee.all():
            return
    messages.warning(request, "Nie masz dostępu do tego projektu")
    return redirect('home')


def home(request):
    if request.user.is_anonymous:
        projects = []
    elif request.user.is_superuser:
        projects = Project.objects.all().order_by("id")
    elif request.user.who_is == "CL":
        client_id = Client.objects.get(user_id=request.user.id)
        projects = Project.objects.filter(client=client_id).order_by('id')
    else:
        employee_id = Employee.objects.get(user_id=request.user.id)
        projects = Project.objects.filter(employee=employee_id).order_by('id')
    context = {'projects': projects}
    return render(request, 'licznik_czasu/home.html', context)


def view_profile(request):
    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Pomyślnie zapisano zmiany")
            return redirect('view_profile')
    else:
        form = UserForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'account/profile.html', context)


@login_required
def view_project(request, project_id):
    check_permissions = can_access_project(request, project_id)
    if check_permissions:
        return check_permissions
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task_name = request.POST.get('task_name')
            description = request.POST.get('description')
            task = Task.objects.create(task_name=task_name, description=description, project_id=project_id)
            messages.success(request, "Pomyślnie dodano zadanie")
            return JsonResponse({"message": "Task added successfully"})
        messages.warning(request, "Nie można było stworzyć nowego zadania")
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
def view_task(request, project_id, task_id):
    check_permissions = can_access_project(request, project_id)
    if check_permissions:
        return check_permissions
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
                messages.success(request, "Pomyślnie zapisano zmiany")
                return JsonResponse({"message": "Task changed successfully"})
            messages.warning(request, "Nie można było zapisać zmian")
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


def delete_task(request, task_id):
    if request.method == "POST":
        task = get_object_or_404(Task, pk=task_id)
        project_id = task.project.pk
        messages.success(request, f"Usunięto zadanie: {task.task_name}")
        task.delete()
        return redirect("view_project", project_id=project_id)
    messages.warning(request, "Brak dostępu do strony")
    return redirect("home")


@login_required
def project_report(request, project_id):
    if request.user.who_is != 'CL' and not request.user.is_superuser:
        messages.warning(request, 'Nie masz dostepu do tej strony.')
        return redirect("view_project", project_id=project_id)

    task_filter = request.POST.get('task_filter', None) # nazwa wybranego filtra zadania
    employee_filter = request.POST.get('employee_filter', None) # nazwa wybranego filtra pracownika

    project = get_object_or_404(Project, pk=project_id)
    tasks = Task.objects.filter(project=project_id)

    last_day = datetime.now() - timedelta(days=1)
    last_week = datetime.now() - timedelta(weeks=1)
    last_month = datetime.now() - timedelta(weeks=4)
    any_date = datetime.min

    flag = True # flaga do wyboru trybu wyświetlania tabeli

    time_filters = {
        'Any date': any_date,
        'Last day': last_day,
        'Last week': last_week,
        'Last month': last_month
    }

    context = {
        'project': project,
        'time_filters': time_filters,
        'task_filter': task_filter,
        'employee_filter': employee_filter,
        'tasks': tasks
    }

    if request.method == 'POST':
        selected_time_filter = request.POST.get('time_filter', None)
        generate_report = request.POST.get('generate_report', None)

        if selected_time_filter is not None: # filtrowanie po czasie
            selected_time_filter_date = time_filters[selected_time_filter]
        else:
            selected_time_filter_date = datetime.min

        tasktimers = [] # lista wszystkich timerów bez względu na taska, dla filtrowania i raportów
        total = timedelta(0) # łączny czas timerów dla filtrowania.

        tasktotal = [] # lista tasków, w celu wyświetlenia podsumowania w tabeli bez filtrowania

        for task in tasks:
            task_time = list(TaskTimer.objects.filter(task=task)) # lista timerów dla konkretnego taska

            tasktimers2 = [] # lista wszystkich timerów dla konkretnego taska
            total2 = timedelta(0) # łączny czas na każdego taska.
            start_dates = [] # daty rozpoczęcia timerów dla konkretnego taska
            end_dates = [] # daty zakończenia timerów dla konkretnego taska

            for time in task_time:
                if time.time_started.date() >= selected_time_filter_date.date(): # filtrowanie po czasie
                    if time.time_elapsed:
                        total2 += time.time_elapsed
                    taskinfo = { # informacje o konkretnym timerze
                        'ids': task.id,
                        'name': time.task.task_name,
                        'time_started': time.time_started,
                        'time_ended': time.time_ended,
                        'time_elapsed': str(time.time_elapsed).split(".")[0],
                        'employee': time.user
                    }

                    # filtrowanie według zadania i pracownika
                    if task_filter != "None" and employee_filter != "None":
                        if task_filter == task.task_name and employee_filter == str(time.user):
                            tasktimers.append(taskinfo)
                            if time.time_elapsed:
                                total += time.time_elapsed
                    elif task_filter != "None" and employee_filter == "None":
                        if task_filter == task.task_name:
                            tasktimers.append(taskinfo)
                            if time.time_elapsed:
                                total += time.time_elapsed
                    elif task_filter == "None" and employee_filter != "None":
                        if employee_filter == str(time.user):
                            tasktimers.append(taskinfo)
                            if time.time_elapsed:
                                total += time.time_elapsed
                    else:
                        tasktimers.append(taskinfo)
                        if time.time_elapsed:
                            total += time.time_elapsed
                        flag = False

                    tasktimers2.append(taskinfo)
                    start_dates.append(time.time_started)
                    if time.time_ended:
                        end_dates.append(time.time_ended)

            if start_dates:
                start_date = min(start_dates)
            else:
                start_date = "-"
            if end_dates:
                end_date = max(end_dates)
            else:
                end_date = "-"

            task3 = { # informacje o konkretnym tasku, w celu wyświetlenia podsumowania
                'task': task,
                'total_elapsed': str(total2).split(".")[0],
                'start': start_date,
                'end': end_date,
                'all_timers': tasktimers2
            }

            tasktotal.append(task3)

        if tasks:
            context = {
                'time_filters': time_filters,
                'project': project,
                'tasks': tasks,
                'tasktimer': tasktimers,
                'time_filter': selected_time_filter,
                'selected_time_filter_date': selected_time_filter_date,
                'tasktotal': tasktotal,
                'task_filter': task_filter,
                'employee_filter': employee_filter,
                'flag': flag,
                'tasktimers_totaltime': str(total).split(".")[0]
            }

        if generate_report is not None:
            template_path = 'licznik_czasu/pdf_template.html'
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="project_report.pdf"'
            template = get_template(template_path)
            html = template.render(context)
            pisa_status = pisa.CreatePDF(html, dest=response, encoding='UTF-8')
            if pisa_status.err:
                return HttpResponse('error')
            return response

    return render(request, 'licznik_czasu/project_report.html', context)


@login_required
def employee_report(request):
    if not request.user.is_superuser:
        return redirect('home')
    employee_table = {}
    context = {
        'employee_table': employee_table,
    }
    if request.method == "POST":
        year = int(request.POST.getlist("year-selector")[0])
        timers = TaskTimer.objects.all()
        time_in_months = [timedelta(0) for _ in range(12)]
        for timer in timers:
            if timer.time_ended and timer.time_ended.year == year:
                employee_table.setdefault(timer.user, time_in_months.copy())
                employee_table[timer.user][timer.time_ended.month-1] += timer.time_elapsed
        # format dict data
        for key, value in employee_table.items():
            for i in range(len(value)):
                if value[i] == timedelta(0):
                    employee_table[key][i] = "X"
                else:
                    employee_table[key][i] = str(employee_table[key][i]).split(".")[0]
        context['year'] = year
    return render(request, 'licznik_czasu/employee_report.html', context)
