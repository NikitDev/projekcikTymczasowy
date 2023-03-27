from django import forms
from .models import User, Project


class UserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProjectForm(forms.ModelForm):
    project_name = forms.CharField(max_length=128, required=True)
    description = forms.CharField(required=True)

    class Meta:
        model = Project
        fields = ['project_name', 'description']
