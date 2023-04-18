from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    who_is = models.CharField(max_length=16, choices=(('CL', 'Client'), ('EM', 'Employee')), default='Client')


class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f'name: {self.user.first_name} {self.user.last_name}, id: {self.id}'


class Project(models.Model):
    project_name = models.TextField(max_length=128)
    description = models.TextField(null=True, blank=True)
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'id: {self.id}'


class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=64, null=True, blank=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'name: {self.user.first_name} {self.user.last_name}, id: {self.id}'


class Task(models.Model):
    task_name = models.TextField(max_length=128)
    description = models.TextField()
    creation_date = models.DateField(auto_now_add=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, default='')


class TaskTimer(models.Model):
    time_started = models.TimeField()
    time_ended = models.TimeField()
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE, default='')
