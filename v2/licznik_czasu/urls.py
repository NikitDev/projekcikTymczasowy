from django.urls import path, include

from . import views

urlpatterns = [
    path('posts', views.posts, name='posts'),
    path('', views.home, name='home'),
    path('accounts/', include('allauth.urls')),
    path('accounts/profile/', views.view_profile, name="view_profile"),
    path('project/create-project/', views.create_project, name="create_project"),
    path('project/<int:project_id>/', views.view_project, name="view_project"),
    path('project/<int:project_id>/edit', views.edit_project, name="edit_project")
]
