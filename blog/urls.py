from django.contrib import admin
from django.urls import path
from .views import index, slug, contentful

urlpatterns = [
    path('', index),
    path('<slug:slug>', slug),
    path('contentful/', contentful)
]
