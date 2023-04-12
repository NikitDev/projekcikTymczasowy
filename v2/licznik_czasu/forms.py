from django import forms
from allauth.account.forms import LoginForm, SignupForm
from .models import User, Project


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control'})


class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['email'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})


class UserForm(forms.ModelForm):
    username = forms.CharField(label="Nazwa użytkownika", disabled=True)
    first_name = forms.CharField(max_length=30, required=True, label="Imię")
    last_name = forms.CharField(max_length=30, required=True, label="Nazwisko")
    email = forms.EmailField(max_length=254, required=True, label="Adres e-mail")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ProjectForm(forms.ModelForm):
    project_name = forms.CharField(max_length=128, required=True, label="Nazwa projektu")
    description = forms.CharField(required=True, label="Opis projektu")

    class Meta:
        model = Project
        fields = ['project_name', 'description']
