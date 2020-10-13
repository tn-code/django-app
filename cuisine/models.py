import os
from datetime import date
from datetime import datetime

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.functions import Lower

from pharmacy.models import Ingredient as Chemical


def get_image_path(self, filename):
    if hasattr(self, 'name'):
        return os.path.join('images', 'cuisine', self.name, filename)
    else:
        return os.path.join('images', 'cuisine', self.dish.name, self.__class__.__name__, filename)


class Season(models.Model):
    name = models.CharField(max_length=32)
    number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)], blank=True, null=True)

    def __str__(self):
        return "{0}. {1}".format(str(self.id), self.name)

    class Meta:
        verbose_name = 'Season'
        verbose_name_plural = 'Seasons'


class Food(models.Model):
    name = models.CharField(max_length=64, unique=True)
    name_en = models.CharField(max_length=64, blank=True, null=True)
    season = models.ManyToManyField(Season)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    recipe = models.OneToOneField(
        'Dish', on_delete=models.PROTECT, blank=True, null=True)
    type = models.ForeignKey(
        'self', on_delete=models.PROTECT, blank=True, null=True)
    chemicals = models.ManyToManyField(
        Chemical, related_name='%(class)ses', blank=True)

    VEGETABLE = 'VEGETABLE'
    FRUIT = 'FRUIT'
    MEAT = 'MEAT'
    PROCESSED_MEAT = 'PROCESSED_MEAT'
    SEAFOOD = 'SEAFOOD'
    DAIRY = 'DAIRY'
    HERB = 'HERB'
    SPICE = 'SPICE'

    CATEGORY_CHOICES = [
        (VEGETABLE, 'Vegetable'),
        (FRUIT, 'Fruit'),
        (MEAT, 'Meat'),
        (PROCESSED_MEAT, 'Processed Meat'),
        (SEAFOOD, 'Seafood'),
        (DAIRY, 'Dairy'),
        (HERB, 'Herb'),
        (SPICE, 'Spice'),
    ]
    category = models.CharField(max_length=32,
                                choices=CATEGORY_CHOICES, blank=True, null=True)

    FOOD = 'FOOD'
    CONDIMENT = 'CONDIMENT'

    CLASSIFICATION_CHOICES = [
        (FOOD, 'Food'),
        (CONDIMENT, 'Condiment'),
    ]
    classification = models.CharField(max_length=32,
                                      choices=CLASSIFICATION_CHOICES, blank=True, null=True)

    def __str__(self):
        return "{0} - {1}".format(self.name_en, self.name)

    class Meta:
        verbose_name = 'Food'
        verbose_name_plural = 'Foods'
        ordering = [Lower('name_en')]


class DishType(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return "{0}. {1}".format(str(self.id), self.name)

    class Meta:
        verbose_name = 'Dish Type'
        verbose_name_plural = 'Dish Types'


class Article(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    foods = models.ManyToManyField(
        Food, related_name='%(class)ses', blank=True)

    def __str__(self):
        return "{0}. {1}".format(str(self.id), self.title)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'


class ArticleImage(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='medicine_images')
    image = models.ImageField(upload_to=get_image_path)
    created_at = models.DateField(auto_now_add=True)
    caption = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return "{id}. {title} [{date}]".format(
            id=str(self.id),
            title=self.article.title,
            date=str(self.created_at)
        )

    class Meta:
        verbose_name = 'Article Image'
        verbose_name_plural = 'Article Images'


class Dish(models.Model):
    name = models.CharField(max_length=64)
    name_alpha = models.CharField(max_length=128, blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    foods = models.ManyToManyField(
        Food, blank=True, symmetrical=False, related_name='%(class)ses', through='Ingredient')

    type = models.ForeignKey(
        DishType, on_delete=models.PROTECT, blank=True, null=True)
    last_created_at = models.DateField(blank=True, null=True)
    cooked_count = models.IntegerField(default=0)
    is_variation = models.BooleanField(default=False)
    variations = models.ForeignKey(
        "self", on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        if self.type:
            return "{0} [{1}]".format(self.name_alpha, self.type.name)
        else:
            return self.name_alpha

    class Meta:
        verbose_name = 'Dish'
        verbose_name_plural = 'Dishes'
        ordering = [Lower('name_alpha')]


class DishImage(models.Model):
    dish = models.ForeignKey(
        Dish, on_delete=models.CASCADE, related_name='dish_images')
    image = models.ImageField(upload_to=get_image_path)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return "{id}. {name} [{date}]".format(
            id=str(self.id),
            name=self.dish.name,
            date=str(self.created_at)
        )

    class Meta:
        verbose_name = 'Dish Image'
        verbose_name_plural = 'Dish Images'


class Recipe(models.Model):
    dish = models.ForeignKey(
        Dish, on_delete=models.CASCADE)
    order = models.IntegerField()
    body = models.CharField(max_length=512)
    image = models.ImageField(
        upload_to=get_image_path, blank=True, null=True)
    tip = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return "{id}. {name} - ({order}) {body}".format(
            id=str(self.id),
            name=self.dish.name_alpha,
            order=str(self.order),
            body=self.body[:20]
        )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'


class IngredientGroup(models.Model):
    name = models.CharField(max_length=64)
    dish = models.ForeignKey(
        Dish, on_delete=models.CASCADE, related_name='%(class)ss')

    def __str__(self):
        return "{0} : {1}".format(self.dish.name_alpha, self.name)

    class Meta:
        verbose_name = 'IngredientGroup'
        verbose_name_plural = 'IngredientGroups'
        ordering = [Lower('name')]


class Ingredient(models.Model):
    dish = models.ForeignKey(
        Dish, on_delete=models.CASCADE, related_name='%(class)ss')
    food = models.ForeignKey(
        Food, on_delete=models.CASCADE, related_name='%(class)ss', blank=True, null=True)
    group = models.ForeignKey(
        IngredientGroup, on_delete=models.CASCADE, related_name='%(class)ss', blank=True, null=True)

    amount = models.IntegerField(blank=True, null=True)

    ENTITY = ''
    GRAM = 'g'
    MILLILITER = 'ml'
    CUP = 'cup'
    TEASPOON = 'tsp.'
    TABLESPOON = 'tbsp.'
    PINCH = 'pinch'
    PIECE = 'piece'
    DROP = 'drop'

    UNIT_CHOICES = [
        (ENTITY, 'entity'),
        (GRAM, 'g'),
        (MILLILITER, 'ml'),
        (CUP, 'cup'),
        (TEASPOON, 'tsp.'),
        (TABLESPOON, 'tbsp.'),
        (PINCH, 'pinch'),
        (PIECE, 'piece'),
        (DROP, 'drop')
    ]
    unit = models.CharField(max_length=32,
                            choices=UNIT_CHOICES, blank=True, null=True)
    alternatives = models.ManyToManyField(
        Food, related_name='alternatives', blank=True)

    def __str__(self):
        return "{id}. {dish} - {food}".format(
            id=str(self.id),
            dish=self.dish.name_alpha,
            food=self.food.name_en
        )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

        constraints = [
            models.UniqueConstraint(
                fields=['dish', 'food', 'group'], name='unique_food_ingredient'),

        ]


class Tea(models.Model):
    name = models.CharField(max_length=64)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    brand = models.CharField(max_length=64)
    country = models.CharField(max_length=64, blank=True, null=True)
    region = models.CharField(max_length=64, blank=True, null=True)
    type = models.CharField(max_length=64, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    tasting = models.TextField(blank=True, null=True)
    last_created_at = models.DateField(blank=True, null=True)
    tasted_count = models.IntegerField(default=0)

    def __str__(self):
        return "{id}. {name} - {brand}".format(
            id=str(self.id),
            name=self.name,
            brand=self.brand
        )

    class Meta:
        verbose_name = 'Tea'
        verbose_name_plural = 'Teas'
