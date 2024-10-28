from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_summaries, name='list_summaries'),
    path('create/', views.create_summary, name='create_summary'),

    path('update/<int:pk>/', views.update_summary, name='update_summary'),
    path('delete/<int:pk>/', views.delete_summary, name='delete_summary'),
]
