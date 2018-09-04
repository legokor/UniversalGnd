from django.urls import path
from . import views


urlpatterns = [
    path('update-item/<int:pk>', views.update_task, name='toggle'),
    path('checklist', views.admin, name='admin'),
    path('upra/flight', views.upra_flight, name='upra_flight'),
    path('upra/com', views.upra_communication, name='upra_communication'),
    path('upra/telemetry', views.upra_telemetry, name='upra_telemetry'),
    path('', views.index, name='index'),
]
