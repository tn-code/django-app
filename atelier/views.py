from datetime import date

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.db.models import Q


def index(request):
    return render(request, 'atelier/index.html')
