from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    who_is = models.CharField(max_length=16, choices=(('CL', 'Client'), ('EM', 'Employee')), default='CL')


class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f'name: {self.user.first_name} {self.user.last_name}, id: {self.id}'


class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f'name: {self.user.first_name} {self.user.last_name}, id: {self.id}'


class Project(models.Model):
    project_name = models.TextField(max_length=128)
    description = models.TextField(null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ManyToManyField(Employee, blank=True)

    def __str__(self):
        return f'project_name: {self.project_name}, id: {self.id}'


class Task(models.Model):
    task_name = models.TextField(max_length=128)
    description = models.TextField()
    creation_date = models.DateField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default='')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)


class TaskTimer(models.Model):
    time_started = models.DateTimeField(auto_now_add=True)
    time_ended = models.DateTimeField(null=True, blank=True)
    time_elapsed = models.DurationField(null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, default='')
