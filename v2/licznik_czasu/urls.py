from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/', include('allauth.urls')),
    path('accounts/profile/', views.view_profile, name="view_profile"),
    path('project/create-project/', views.create_project, name="create_project"),
    path('project/<int:project_id>/', views.view_project, name="view_project"),
    path('project/<int:project_id>/task/<int:task_id>/', views.view_task, name="view_task"),
    path('project/<int:project_id>/', views.view_project, name="view_project"),
    path('project/<int:project_id>/report' , views.project_report, name="project_report" ),
    path('report/', views.project_report, name="project_report")
]
