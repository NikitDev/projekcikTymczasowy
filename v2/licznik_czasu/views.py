from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from weasyprint import HTML
from .models import Project, Task, TaskTimer, Client, Employee
from .forms import UserForm, TaskForm, TaskEmployeeForm
from django import forms
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
from calendar import monthrange


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
def client_data(request, project_id, task_id):
    data = TaskTimer.objects.filter(is_active=True, task_id=task_id)
    dane = []
    for osoba in data:
        dane.append({
            'imie': osoba.user.first_name,
            'nazwisko': osoba.user.last_name
        })
    return JsonResponse(dane, safe=False)


@csrf_exempt
@require_POST
def save_view(request, project_id, task_id):
    print("XDDDDDDD")
    if request.method == "POST":
        start_time = timezone.datetime.fromtimestamp(float(request.session.get('start_time')))
        end_time = timezone.datetime.fromtimestamp(float(timezone.now().timestamp()))
        duration = end_time - start_time
        timer = TaskTimer.objects.get(pk=request.session.get('pk'), user=request.user)
        timer.time_ended = end_time
        timer.time_elapsed = duration
        timer.is_active = False
        timer.save()
        request.session['start_time'] = None
        return HttpResponse(status=200)


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
            timer = TaskTimer.objects.create(task_id=task_id, user=request.user, is_active=True)
            request.session['pk'] = timer.pk
            return JsonResponse({'success': True})
        elif action == 'stop':
            save_view(request, project_id, task_id)
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
        'current': request.session.get('start_time'),
        'who_is': str(request.user.who_is),
        'is_superuser': bool(request.user.is_superuser)
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

        tasktimers = [] # lista wszystkich timerów bez względu na taska; dla wyświetlania filtrowania i raportów pdf
        total = timedelta(0) # łączny czas timerów po zastosowaniu filtrowania

        tasktotal = [] # lista tasków; w celu wyświetlenia podsumowania w rozwijanej tabeli, bez filtrowania

        for task in tasks:
            task_time = list(TaskTimer.objects.filter(task=task)) # lista timerów dla konkretnego taska

            tasktimers2 = [] # lista wszystkich timerów dla konkretnego taska
            total2 = timedelta(0) # łączny czas na każdego taska
            start_dates = [] # daty rozpoczęcia timerów dla konkretnego taska; żeby wybrać pierwszą
            end_dates = [] # daty zakończenia timerów dla konkretnego taska; żeby wybrąć ostatnią

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

            task3 = { # informacje o konkretnym tasku; w celu wyświetlenia podsumowania
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
            template = get_template(template_path)
            html = template.render(context)

            pdf = HTML(string=html).write_pdf()

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="project_report.pdf"'
            response.write(pdf)

            return response

    return render(request, 'licznik_czasu/project_report.html', context)


@login_required
def employee_report(request):
    if not request.user.is_superuser:
        messages.warning(request, 'Nie masz dostepu do tej strony.')
        return redirect('home')
    if request.method == "POST":
        generate_report = request.POST.get('generate_report', None) #pobieranie wartości generate report
        employee_table = {}
        year = int(request.POST.getlist("year-selector")[0])
        month = int(request.POST.getlist("month-selector")[0])
        days = 0
        if month == 0:
            flag = "year"
            timers = TaskTimer.objects.all()
            time_in_months = [timedelta(0) for _ in range(12)]
            for timer in timers:
                if timer.time_ended and timer.time_ended.year == year:
                    employee_table.setdefault(timer.user, time_in_months.copy())
                    employee_table[timer.user][timer.time_ended.month-1] += timer.time_elapsed
        else:
            flag = "month"
            days = monthrange(year, month)[1]
            timers = TaskTimer.objects.all()
            time_in_days = [timedelta(0) for _ in range(days)]
            for timer in timers:
                if timer.time_ended and timer.time_ended.year == year and timer.time_ended.month == month:
                    employee_table.setdefault(timer.user, time_in_days.copy())
                    employee_table[timer.user][timer.time_ended.day-1] += timer.time_elapsed
        # format dict data
        for key, value in employee_table.items():
            for i in range(len(value)):
                if value[i] == timedelta(0):
                    employee_table[key][i] = "X"
                else:
                    time_seconds = employee_table[key][i].total_seconds()
                    time_hours = time_seconds // 3600
                    time_minutes = time_seconds % 3600 // 60
                    employee_table[key][i] = f"{time_hours:g}h {time_minutes:g}m"

        context = {
            'employee_table': employee_table,
            'year': year,
            'month': month,
            'days': range(days),
            'flag': flag
        }
        if generate_report is not None: #przy pobraniu wartości generate_report
            template_path = 'licznik_czasu/employee_report_pdf.html' #link do tamplate pdf
            template = get_template(template_path)
            html = template.render(context)

            pdf = HTML(string=html).write_pdf()

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="employee_report.pdf"' #nazwa wygenerowanego pliku / nie jest zapisywany
            response.write(pdf)

            return response #po wygenerowaniu raportu od razu go otwiera

    else:
        context = {}
    return render(request, 'licznik_czasu/employee_report.html', context)
