from django.contrib import admin
from .models import Dish, Food, Recipe, DishType, Season, Ingredient,  DishImage, Tea, IngredientGroup, Article, ArticleImage
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline


admin.site.register(Recipe)
admin.site.register(DishType)
admin.site.register(Season)
admin.site.register(Ingredient)
admin.site.register(IngredientGroup)
admin.site.register(Tea)


class FoodAdmin(NestedModelAdmin):
    search_fields = ('name',)


admin.site.register(Food, FoodAdmin)


class ArticleImageInline(NestedTabularInline):
    model = ArticleImage
    extra = 0


class ArticleAdmin(NestedModelAdmin):
    search_fields = ('name',)
    inlines = [ArticleImageInline]


admin.site.register(Article, ArticleAdmin)


class IngredientInline(NestedTabularInline):
    model = Ingredient
    extra = 0


class DishImageInline(NestedTabularInline):
    model = DishImage
    extra = 0


class RecipeInline(NestedTabularInline):
    model = Recipe
    extra = 0


class DishAdmin(NestedModelAdmin):
    search_fields = ('name',)
    inlines = [IngredientInline, RecipeInline, DishImageInline]


admin.site.register(Dish, DishAdmin)
