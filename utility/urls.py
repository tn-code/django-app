from django.contrib import admin
from django.urls import path, include
from .views import index, schedules, schedule, todos


urlpatterns = [
    path('', index, name="index"),
    path('schedules/', schedules, name="schedules"),
    path('schedules/<int:pk>/', schedule, name="schedule"),
    path('todos/', todos, name="todos")

]
