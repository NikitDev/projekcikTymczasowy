from django.contrib import admin
from django.forms import ModelForm, RadioSelect, ChoiceField

from .models import Client, Project, Employee, Task, TaskTimer, User

# Register your models here.
admin.site.register(Client)
admin.site.register(Project)
admin.site.register(Employee)
admin.site.register(Task)
admin.site.register(TaskTimer)
admin.site.register(User)
