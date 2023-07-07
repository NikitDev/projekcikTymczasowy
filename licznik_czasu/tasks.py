from celery import shared_task
from taiga import TaigaAPI
import os

from .models import Project, Employee, Task, User


@shared_task(serializer='json')
def get_taiga(user_id, user_first_name, user_last_name):
    api = TaigaAPI(
        host='https://taiga.webtechnika.pl'
    )
    api.auth(
        username='Nikit',
        password=os.getenv('PASSWORD')
    )

    request_employee = Employee.objects.get(user_id=user_id)
    user_projects_query = request_employee.project_set.all().values_list('taiga_id', flat=True)
    user_projects_list = list(user_projects_query)
    taiga_projects_list = api.projects.list()
    taiga_users = api.users.list()

    user_full_name = user_first_name + ' ' + user_last_name

    for i in taiga_projects_list:
        if i.id not in user_projects_list:
            for taiga_user in i.list_memberships():
                if str(taiga_user.full_name) == str(user_full_name):
                    if not Project.objects.filter(taiga_id=i.id).exists():
                        Project.objects.create(project_name=i.slug, description=i.description, taiga_id=i.id)

                    employee = Employee.objects.get(user_id=user_id)
                    project = Project.objects.get(taiga_id=i.id)
                    user_projects_list.append(i.id)

                    project.employee.add(employee)
                    break
        else:
            for task in i.list_user_stories():
                taiga_members = []
                for member in task.assigned_users:
                    for taiga_m in taiga_users:
                        if member == taiga_m.id:
                            taiga_members.append(taiga_m.full_name)
                try:
                    project_for_tasks = Project.objects.get(taiga_id=i.id)
                except Project.DoesNotExist:
                    continue
                if task.id not in project_for_tasks.task_set.all().values_list('taiga_task_id', flat=True):
                    task_tracker = Task.objects.get_or_create(
                        task_name=task,
                        description=i.get_userstory_by_ref(task.ref).description,
                        project=project_for_tasks,
                        taiga_task_id=task.id
                    )
                    task_tracker = Task.objects.get(taiga_task_id=task.id)
                    taiga_members = list(map(str, taiga_members))
                    if str(user_full_name) in taiga_members:
                        usr = User.objects.get(first_name=user_first_name, last_name=user_last_name)
                        employee = Employee.objects.get(user=usr.id)
                        task_tracker.employee.add(employee.id)

    return {"status": True}


@shared_task(serializer='json')
def get_taiga_admin():
    api = TaigaAPI(
        host='https://taiga.webtechnika.pl'
    )
    api.auth(
        username='Nikit',
        password=os.getenv('PASSWORD')
    )

    all_projects_query = Project.objects.all().values_list('taiga_id', flat=True)
    all_projects_list = list(all_projects_query)
    taiga_projects_list = api.projects.list()
    taiga_users = api.users.list()

    # user_full_name = request.user.first_name + ' ' + request.user.last_name

    for i in taiga_projects_list:
        if i.id not in all_projects_list:
            for taiga_user in i.list_memberships():
                if not Project.objects.filter(taiga_id=i.id).exists():
                    Project.objects.create(project_name=i.slug, description=i.description, taiga_id=i.id)

                first_name, last_name = taiga_user.full_name.split()
                employee = Employee.objects.get(first_name=first_name, last_name=last_name)
                project = Project.objects.get(taiga_id=i.id)
                all_projects_list.append(i.id)
                project.employee.add(employee)

        else:
            for task in i.list_user_stories():
                taiga_members = []
                for member in task.assigned_users:
                    for taiga_m in taiga_users:
                        if member == taiga_m.id:
                            taiga_members.append(taiga_m.full_name)
                try:
                    project_for_tasks = Project.objects.get(taiga_id=i.id)
                except Project.DoesNotExist:
                    continue
                if task.id not in project_for_tasks.task_set.all().values_list('taiga_task_id', flat=True):
                    task_tracker = Task.objects.create(
                        task_name=task,
                        description=i.get_userstory_by_ref(task.ref).description,
                        project=project_for_tasks,
                        taiga_task_id=task.id
                    )

                    taiga_members = list(map(str, taiga_members))
                    for member in taiga_members:
                        first_name, last_name = member.full_name.split()
                        usr = User.objects.get(first_name=first_name, last_name=last_name)
                        employee = Employee.objects.get(user=usr.id)
                        task_tracker.employee.add(employee.id)
