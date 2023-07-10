from django import forms
from allauth.account.forms import LoginForm, SignupForm, ChangePasswordForm, ResetPasswordForm
from django.contrib.auth.forms import UserChangeForm

from .models import User, Project, Task, Employee


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'login'})
        self.fields['password'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'password'})


class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'username'})
        self.fields['email'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'email'})
        self.fields['password1'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'password1'})
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'password2'})


class CustomChangePasswordForm(ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['oldpassword'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'oldpassword'})
        self.fields['password1'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'password1'})
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'password2'})


class CustomResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email'})


class UserForm(forms.ModelForm):
    username = forms.CharField(label="Nazwa użytkownika", disabled=True)
    username.widget = forms.TextInput(attrs={'class': 'form-control'})
    first_name = forms.CharField(max_length=30, required=True, label="Imię")
    first_name.widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'name'})
    last_name = forms.CharField(max_length=30, required=True, label="Nazwisko")
    last_name.widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'last_name'})
    email = forms.EmailField(max_length=254, required=True, label="Adres e-mail")
    email.widget = forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email'})

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class TaskForm(forms.ModelForm):
    task_name = forms.CharField(max_length=30, label="Nazwa zadania")
    task_name.widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwa nowego zadania'})
    description = forms.CharField(label="Opis zadania", required=False)
    description.widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opis nowego zadania'})

    class Meta:
        model = Task
        fields = ['task_name', 'description']


class TaskEmployeeForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['employee']


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class CustomTaigaLoginForm(forms.Form):
    # username = forms.TextInput()
    # username.widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'login'})
    # password = forms.TextInput()
    # password.widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'password'})
    login = forms.CharField(label="Login")
    haslo = forms.CharField(label="Haslo", widget=forms.PasswordInput)

