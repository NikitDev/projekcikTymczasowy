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
        return f'Client: {self.user.username}, id: {self.id}'


class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f'Employee: {self.user.username}, id: {self.id}'


class Project(models.Model):
    project_name = models.TextField(max_length=128)
    description = models.TextField(null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    employee = models.ManyToManyField(Employee, blank=True)

    def __str__(self):
        return self.project_name


class Task(models.Model):
    task_name = models.TextField(max_length=128)
    description = models.TextField()
    creation_date = models.DateField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default='')
    employee = models.ManyToManyField(Employee, blank=True)
    status = models.TextField(default="New")

    def __str__(self):
        return self.task_name


class TaskTimer(models.Model):
    time_started = models.DateTimeField(auto_now_add=True)
    time_ended = models.DateTimeField(null=True, blank=True)
    time_elapsed = models.DurationField(null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, default='')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default='')
    is_active = models.BooleanField(default=False, null=True, blank=True)
