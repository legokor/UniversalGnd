from django.urls import path
from . import views


urlpatterns = [
    path('toggle-item/<int:id>', views.toggle, name='toggle'),
    path('checklist', views.admin, name='admin'),
    path('', views.index, name='index'),
]
