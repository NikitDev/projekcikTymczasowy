from django.contrib import admin

from .models import Client, Project, Employee, Task, TaskTimer

# Register your models here.
admin.site.register(Client)
admin.site.register(Project)
admin.site.register(Employee)
admin.site.register(Task)
admin.site.register(TaskTimer)

