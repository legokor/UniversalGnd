from django.urls import path
from . import views

urlpatterns = [
    path('checklist', views.checklist, name='checklist'),
    path('toggle-item/<int:id>', views.toggle, name='toggle'),
    path('admin', views.admin, name='admin'),
    path('', views.index, name='index'),
]
