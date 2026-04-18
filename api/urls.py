from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('projects/', views.api_projects, name='projects'),
    path('projects/<int:project_pk>/datasets/', views.api_datasets, name='datasets'),
    path('projects/<int:project_pk>/results/', views.api_results, name='results'),
    path('results/<int:pk>/', views.api_result_detail, name='result_detail'),
]
