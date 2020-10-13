from django.contrib import admin
from django.urls import path
from .views import index, dish, dishes, add_dish, dish_count, type, ingredients, food, condiment, get_svg, teas, search


urlpatterns = [
    path('', index, name="index"),
    path('search', search, name="search"),
    path('dishes/', dishes, name="dishes"),
    path('dishes/<int:pk>', dish, name="dish"),
    path('dishes/new', add_dish, name="dish_add"),
    path('dishes/<int:pk>/count', dish_count, name="dish_count"),
    path('dishes/types/<int:pk>', type, name="type"),
    path('ingredients/', ingredients, name="ingredients"),
    path('ingredients/foods/<int:pk>', food, name="food"),
    path('ingredients/condiments/<int:pk>', condiment, name="condiment"),
    path('teas/', teas, name="teas"),
    path('plots/', get_svg, name="plots")
]
