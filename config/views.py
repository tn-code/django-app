
import datetime
import json
import requests
import xml.etree.ElementTree as ET


from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django import template
from django.db.models import Q
from django.contrib.auth.models import User

from cuisine.models import Dish, Food, Recipe
from arts.models import Exhibition, Work, Artist, Genre
from cuisine.models import Dish
from lib.models import Book, Quote, Theme
from en.models import Term, Sentence
from utility.models import Todo, Bookmark
from arts.models import Work


def index(request):
    todos = Todo.objects.all()
    work = Work.objects.order_by('?').first()
    bookmarks = Bookmark.objects.all().order_by('id')
    context = {
        'todos': todos,
        'work': work,
        'bookmarks': bookmarks
    }
    return render(request, 'index.html', context)


def about(request):
    return render(request, 'pages/about.html')


def calender(request):
    return render(request, 'pages/calendar.html')


def calender_detail(request, year, month, day):

    days = []
    for i in range(1, 8):
        days.append(i)

    times = []
    for i in range(0, 24):
        times.append(str(i) + ' - ' + str(i + 1))

    context = {
        'year': year,
        'month': month,
        'day': day,
        'days': days,
        'times': times
    }
    return render(request, 'pages/schedule.html', context)


def search(request):
    q = request.GET.get('q')
    books = Book.objects.filter(name__contains=q)
    quotes = Quote.objects.filter(body__contains=q)
    themes = Theme.objects.filter(name__contains=q)
    try:
        food = Food.objects.get(name__contains=q)
        dishes_f = food.dish_set.all()
    except:
        dishes_f = None
        food = None

    dishes_n = Dish.objects.filter(name__contains=q)
    works = Work.objects.filter(title_jp__contains=q)
    exhibitions = Exhibition.objects.filter(name__contains=q)
    artists = Artist.objects.filter(name__contains=q)
    genres = Genre.objects.filter(name__contains=q)
    terms = Term.objects.filter(name__contains=q).exclude(
        is_basic=True, is_advanced=False)
    sentences = Sentence.objects.filter(body__contains=q)

    if books.count() > 0 or quotes.count() > 0 or themes.count() > 0 or dishes_n.count() > 0 or dishes_f is not None or works.count() > 0 or exhibitions.count() > 0 or artists.count() > 0 or genres.count() > 0:
        flag = True
    else:
        flag = False

    return render(request, 'pages/search.html', {
        'query': q,
        'books': books,
        'quotes': quotes,
        'themes': themes,
        'dishes_n': dishes_n,
        'dishes_f': dishes_f,
        'works': works,
        'exhibitions': exhibitions,
        'artists': artists,
        'genres': genres,
        'food': food,
        'terms': terms,
        'sentences': sentences,
        'flag': flag
    })
