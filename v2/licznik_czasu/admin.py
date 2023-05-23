from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserChangeForm
from .models import Client, Project, Employee, Task, TaskTimer, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'who_is')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'who_is', 'is_staff'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom fields', {'fields': ('who_is',)}),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'project_description', 'client')

    def project_description(self, obj):
        return obj.description[:30] + '...' if len(obj.description) > 30 else obj.description


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'phone_number')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'task_description', 'creation_date', 'project')

    def task_description(self, obj):
        return obj.description[:30] + '...' if len(obj.description) > 30 else obj.description


@admin.register(TaskTimer)
class TaskTimerAdmin(admin.ModelAdmin):
    list_display = ('time_started', 'time_ended', 'time_elapsed', 'task')
