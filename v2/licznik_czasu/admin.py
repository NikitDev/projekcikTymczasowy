from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password
from .models import Client, Project, Employee, Task, TaskTimer, User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + ('password', 'first_name', 'last_name', 'who_is',)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm

    def save_model(self, request, obj, form, change):
        password = make_password(form.cleaned_data.get("password"), hasher="pbkdf2_sha256")
        print(password)
        obj.password = password
        obj.save()


# Register your models here.
admin.site.register(Client)
admin.site.register(Project)
admin.site.register(Employee)
admin.site.register(Task)
admin.site.register(TaskTimer)
admin.site.register(User, CustomUserAdmin)
