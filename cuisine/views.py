import io
import numpy as np
from datetime import date
try:
    import matplotlib
    matplotlib.use('Agg')
finally:
    from matplotlib import pyplot as plt
import datetime
import time
import urllib.request
import urllib.error
import math
import collections
import statistics


from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.db.models import Q

from .models import Dish, Food, Recipe, Ingredient, DishType, DishImage, Tea, IngredientGroup
from lib.models import Memo
from .forms import DishForm


dishes_query = (Q(type=8) | Q(type=9) | Q(type=10))


def search(request):
    if request.method == 'GET' and request.GET.get('q'):
        q = request.GET.get('q')
        foods = Food.objects.filter(name__contains=q)
        dishes_ls = [f.dishes.all() for f in foods if foods]

        return render(request, 'cuisine/search.html',
                      {
                          'title': '「' + q + '」の検索結果',
                          'dishes_ls': dishes_ls,
                          'query': q,
                          'foods': foods
                      })


def index(request):
    total = Dish.objects.all().count()
    memos = Memo.objects.filter(category='CUISINE').order_by('?')[:5]

    if request.method == 'GET':
        if request.GET.get('q'):
            q = request.GET.get('q')
            foods = Food.objects.filter(name__contains=q)
            dishes_ls = [f.dish_set.all() for f in foods if foods]

            context = {
                'title': '「' + q + '」の検索結果',
                'dishes_ls': dishes_ls,
                'query': q,
                'foods': foods
            }

            return render(request, 'cuisine/search.html', context)

        else:
            dishes = Dish.objects.all().order_by('-id')[:4]
            month = date.today().strftime('%B')
            seasonal_foods = Food.objects.filter(season__name=month).first()
            if seasonal_foods:
                seasonals = Dish.objects.filter(
                    foods__name__contains=seasonal_foods.name).order_by('?')[:5]
            else:
                seasonals = []

            context = {
                'title': 'Cuisine',
                'dishes': dishes,
                'seasonals': seasonals,
                'month': month,
                'seasonal_foods': seasonal_foods,
                'memos': memos,
                'total': total
            }

            return render(request, 'cuisine/index.html', context)

    else:
        dishes = Dish.objects.all().order_by(
            '-id').exclude(dishes_query)[:4]
        month = date.today().strftime('%B')
        seasonal_foods = Food.objects.filter(season__name=month).first()
        seasonals = Dish.objects.filter(
            foods__name__contains=seasonal_foods.name).order_by('?')[:5]

        context = {
            'title': 'Cuisine',
            'dishes': dishes,
            'seasonals': seasonals,
            'month': month,
            'seasonal_foods': seasonal_foods,
            'memos': memos
        }

        return render(request, 'cuisine/index.html', context)


def add_dish(request):
    form = DishForm(request.POST, files=request.FILES or None)
    context = {'form': form}
    RecipeFormset = DishForm.RecipeFormset
    context['foods'] = Food.objects.filter(
        classification='FOOD').order_by('name_en')
    context['condiments'] = Food.objects.filter(
        classification='CONDIMENT').order_by('name_en')
    if request.method == 'POST' and form.is_valid():
        dish = form.save(commit=False)
        formset = RecipeFormset(
            request.POST, files=request.FILES, instance=dish)
        if formset.is_valid():
            dish.save()
            try:
                for pk in request.POST.getlist('food_pks[]'):
                    food = Food.objects.get(id=pk)
                    dish.foods.add(food)
            except:
                pass
            try:
                for pk in request.POST.getlist('condiment_pks[]'):
                    condiment = Food.objects.get(id=pk)
                    dish.foods.add(condiment)
            except:
                pass
            formset.save()

            messages.success(request, 'New dish 「' +
                             dish.name + '」has been added successfully')

            return redirect('cuisine:index')
        else:
            context['formset'] = formset

    else:
        context['formset'] = RecipeFormset()

    return render(request, 'cuisine/add_dish.html', context)


def type(request, pk):
    type = DishType.objects.get(id=pk)
    dishes = Dish.objects.filter(type=type)

    context = {
        'dishes': dishes,
        'type': type
    }
    return render(request, 'cuisine/dishes.html', context)


def ingredients(request):
    foods = Food.objects.filter(classification='FOOD').order_by('name_en')
    condiments = Food.objects.filter(
        classification='CONDIMENT').order_by('name_en')
    ingredients = foods.union(condiments)

    context = {
        'foods': foods,
        'condiments': condiments,
        'ingredients': ingredients
    }

    return render(request, 'cuisine/ingredients.html', context)


def food(request, pk):
    context = {}
    context['ingredient'] = Food.objects.get(id=pk)

    return render(request, 'cuisine/ingredient.html', context)


def condiment(request, pk):
    context = {}
    context['ingredient'] = Food.objects.get(id=pk)

    return render(request, 'cuisine/ingredient.html', context)


def teas(request):
    teas = Tea.objects.all()
    context = {
        'teas': teas
    }
    return render(request, 'cuisine/teas.html', context)


def dishes(request):
    dishes = Dish.objects.all().order_by('-id')
    mains = dishes.filter(type=6)
    sides = dishes.filter(type=3)
    salads = dishes.filter(type=1)
    desserts = dishes.filter(type=5)
    one_bowls = dishes.filter(type=2)
    bases = dishes.filter(type__in=[8, 9, 10])
    soups = dishes.filter(type=11)

    return render(request, 'cuisine/dishes.html',
                  {
                      'title': 'Dishes',
                      'mains': mains,
                      'sides': sides,
                      'salads': salads,
                      'desserts': desserts,
                      'one_bowls': one_bowls,
                      'bases': bases,
                      'soups': soups
                  })


def dish(request, pk):
    dish = Dish.objects.get(id=pk)
    # Note that 'exclude' returns a new QuerySet containing objects that do NOT match the given lookup parameters
    ingredients = Ingredient.objects.filter(
        dish_id=dish.id)

    dish_images = DishImage.objects.filter(dish=pk).order_by('created_at')
    return render(request, 'cuisine/dish.html',
                  {
                      'title': dish.name,
                      'dish': dish,
                      'ingredients': ingredients,
                      'dish_images': dish_images
                  })


def dish_count(request, pk):
    dish = get_object_or_404(Dish, id=pk)
    dish.last_created_at = date.today()
    dish.cooked_count += 1
    dish.save(update_fields=["last_created_at", "cooked_count"])
    return redirect('cuisine:dish', pk=dish.id)


def get_types(dishes):
    items = [d.type.name for d in dishes if d.type]
    # Counter returns a dict with given value as keys and numbers as values
    collection = collections.Counter(items)
    return collection


def getFig():
    dishes = Dish.objects.all()
    collection = get_types(dishes)

    # Convert dict to list that contains keys(type names)
    types = list(collection)
    # Extract values(counts) in the dict
    counts = list(collection.values())

    type_list = np.array(types)
    count_list = np.array(counts)

    c_cycle = ("#3498db", "#51a62d", "#1abc9c", "#9b59b6", "#f1c40f",
               "#7f8c8d", "#34495e", "#446cb3", "#d24d57", "#27ae60",
               "#663399", "#f7ca18", "#bdc3c7", "#2c3e50", "#d35400",
               "#9b59b6", "#ecf0f1", "#ecef57", "#9a9a00", "#8a6b0e")

    fig, (ax1, ax2) = plt.subplots(figsize=(
        10, 4), nrows=1, ncols=2, dpi=80, facecolor='w', edgecolor='k')
    ax1.set(xlabel='Dish Types', title='Dish Type Stats.')
    ax1.grid()

    ax1.pie(count_list, labels=type_list,
            colors=c_cycle,
            wedgeprops={'linewidth': 1, 'edgecolor': "white"},
            textprops={'color': "black", 'weight': "normal"},
            startangle=90,
            counterclock=False,
            autopct=lambda p: '{:.1f}%'.format(p) if p >= 5 else '',
            pctdistance=0.7
            )
    ax2.barh(type_list, count_list)
    ax2.grid()

    # ax1.legend(loc="center right", bbox_to_anchor=(0,.5,1.5,0),)

    return fig


def get_svg(request):

    fig = getFig()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200)
    plt.close(fig)
    response = HttpResponse(buf.getvalue(), content_type='image/png')
    return response
