from django.contrib import admin
from django.urls import path, include
from .views import index, term, term_add, usages, usage, search

urlpatterns = [
    path('', index, name="index"),
    path('terminos/<int:pk>', term, name="term"),
    path('terminos/anadir', term_add, name="term_add"),
    path('usos/', usages, name="usages"),
    path('usos/<int:pk>/', usage, name="usage"),
    path('search', search, name="search"),
]
