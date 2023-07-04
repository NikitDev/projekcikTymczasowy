from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/', include('allauth.urls')),
    path('accounts/profile/', views.view_profile, name="view_profile"),
    path('project/<int:project_id>/', views.view_project, name="view_project"),
    path('project/<int:project_id>/task/<int:task_id>/', views.view_task, name="view_task"),
    path('project/<int:project_id>/report', views.project_report, name="project_report"),
    path('employee-report', views.employee_report, name='employee_report'),
    path('delete-task/<int:task_id>', views.delete_task, name="delete_task"),
    path('project/<int:project_id>/task/<int:task_id>/save_view/', views.save_view, name="save_view"),
    path('project/<int:project_id>/task/<int:task_id>/save_view_second/', views.save_view_second, name="save_view_second"),
    path('project/<int:project_id>/task/<int:task_id>/active/', views.client_data, name='active_employees'),

]
