from django.urls import path
from . import views


urlpatterns = [
    path('update-item/<int:pk>', views.update_task, name='toggle'),
    path('checklist', views.admin, name='admin'),
    # path('hab/<slug:team>/<slug:mission>/tasks', views.hab_gnd, name='hab_tasks'),
    path('hab/<slug:team>/<slug:mission>/', views.hab_gnd, name='hab_gnd'),
    # path('rvr/<slug:team>/<slug:mission>/tasks', views., name='rover_tasks'),
    path('rvr/<slug:team>/<slug:mission>/', views.rover_gnd, name='rover_gnd'),
    # path('drn/<slug:team>/<slug:mission>/tasks', views., name='drone_tasks'),
    path('drn/<slug:team>/<slug:mission>/', views.drone_gnd, name='drone_gnd'),
    path('', views.index, name='index'),
]
