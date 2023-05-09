from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Client, Project, Employee, Task, TaskTimer, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'who_is')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'who_is', 'is_staff'),
        }),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'description', 'client')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'phone_number')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'description', 'creation_date', 'project')


@admin.register(TaskTimer)
class TaskTimerAdmin(admin.ModelAdmin):
    list_display = ('time_started', 'time_ended', 'time_elapsed', 'task')
