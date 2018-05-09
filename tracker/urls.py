from django.urls import path
from . import views


urlpatterns = [
    path('update-item/<int:pk>', views.update_task, name='toggle'),
    path('checklist', views.admin, name='admin'),
    path('', views.index, name='index'),
]
