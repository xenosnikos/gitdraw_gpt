from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('add_repository/', views.add_repository, name='add_repository'),
    path('sync_repo/<int:repo_id>/', views.sync_repo, name='sync_repo'),
    path('generate_diagram/<int:repo_id>/', views.generate_diagram, name='generate_diagram'),
]
