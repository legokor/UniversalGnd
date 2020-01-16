from django.urls import path
from . import views


urlpatterns = [
    path('update-item/<int:pk>', views.update_task, name='toggle'),
    path('checklist', views.admin, name='admin'),
    path('hab/<slug:team_slug>/<slug:mission_slug>/', views.hab_gnd, name='hab_gnd'),
    path('rvr/<slug:team_slug>/<slug:mission_slug>/', views.rover_gnd, name='rover_gnd'),
    path('drn/<slug:team_slug>/<slug:mission_slug>/', views.drone_gnd, name='drone_gnd'),
    path('', views.index, name='index'),
]
