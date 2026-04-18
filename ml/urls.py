from django.urls import path
from . import views

app_name = 'ml'

urlpatterns = [
    path('select/<int:dataset_pk>/', views.model_select, name='select'),
    path('train/<int:dataset_pk>/', views.model_train, name='train'),
    path('result/<int:pk>/', views.model_result, name='result'),
    path('result/<int:pk>/delete/', views.result_delete, name='result_delete'),
    path('result/<int:pk>/export/', views.result_export, name='result_export'),
    path('compare/<int:project_pk>/', views.model_compare, name='compare'),
    path('suggest/<int:dataset_pk>/', views.model_suggest, name='suggest'),
]
