from django.urls import path
from . import views

app_name = 'datasets'

urlpatterns = [
    path('upload/<int:project_pk>/', views.dataset_upload, name='upload'),
    path('<int:pk>/preview/', views.dataset_preview, name='preview'),
    path('<int:pk>/stats/', views.dataset_stats, name='stats'),
    path('<int:pk>/missing/', views.dataset_handle_missing, name='handle_missing'),
    path('<int:pk>/delete/', views.dataset_delete, name='delete'),
    path('<int:pk>/columns/', views.dataset_columns, name='columns'),
]
