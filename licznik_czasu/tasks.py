import json

import requests

from celery import shared_task
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from taiga import TaigaAPI

from .models import Project, Employee, Task, User


def create_periodic_task(user_id):
    print('aha')
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=30,
        period=IntervalSchedule.SECONDS,
    )
    print("XDDDDD")
    pr, _ = PeriodicTask.objects.get_or_create(
        interval=schedule,
        task='licznik_czasu.tasks.get_taiga',
        name=f'Periodic Task for User ID: {user_id}',
        args=json.dumps([user_id]),
    )
    print(f'koniec:')


@shared_task
def authenticate_taiga_user(user_id, username, password):
    try:
        api = TaigaAPI(
            host='https://taiga.webtechnika.pl'
        )
        api.auth(
            username=username,
            password=password
        )
        auth_token = api.token
        refresh_token = api.token_refresh

        user = User.objects.get(id=user_id)
        user.auth_token = auth_token
        user.refresh_token = refresh_token
        user.save()
        print('Success')
        create_periodic_task(user_id)
    except Exception as e:
        print(e)


@shared_task
def get_taiga(user_id):
    try:
        api = TaigaAPI(
            host='https://taiga.webtechnika.pl',
            token=User.objects.get(id=user_id).auth_token
        )
        assert api.me()
    except:
        user = User.objects.get(id=user_id)
        response = requests.post(
                'https://taiga.webtechnika.pl/api/v1/auth/refresh',
                json={
                    'grant_type': 'refresh_token',
                    'refresh': user.refresh_token
                }
            ).json()

        user.auth_token = response['auth_token']
        user.refresh_token = response['refresh_token']
        user.save()

        return 'Error...'

    print("Task started...")

    taiga_projects = [project for project in api.projects.list()]
    user_taiga_id = api.me().id
    user_to_add = User.objects.get(id=user_id)
    employee_to_add = Employee.objects.get(user_id=user_to_add.id)

    for taiga_project in taiga_projects:
        project, _ = Project.objects.update_or_create(
            project_name=taiga_project.name,
            taiga_project_id=taiga_project.id,
            defaults={
                'description': taiga_project.description
            }
        )
        if not project.employee.filter(id=user_to_add.id).exists():
            project.employee.add(employee_to_add.id)

        taiga_project_tasks = [task for task in taiga_project.list_user_stories()]
        for taiga_task in taiga_project_tasks:
            description = taiga_project.get_userstory_by_ref(taiga_task.ref).description
            task, _ = Task.objects.update_or_create(
                task_name=taiga_task.subject,
                taiga_task_id=taiga_task.id,
                defaults={
                    'description': description,
                    'project': project
                }
            )
            if user_taiga_id in taiga_task.assigned_users:
                if not task.employee.filter(id=user_to_add.id).exists():
                    task.employee.add(employee_to_add.id)

    print("Task ended...")
