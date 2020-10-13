import random
import datetime
import json

from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models.functions import Lower
from django.forms.models import model_to_dict
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models.functions import Lower
from django.utils.html import format_html

from .forms import TermForm, SentenceForm
from .models import Term, Sentence, Definition, Usage


def index(request):
    usages = Usage.objects.all()
    todays = Term.objects.filter(created_at=datetime.date.today())
    pickup = Sentence.objects.order_by('?').first()
    total = Term.objects.all().count()

    context = {
        'usages': usages,
        'todays': todays,
        'pickup': pickup,
        'total': total,
    }

    return render(request, 'es/index.html', context)


def term(request, pk):
    term = Term.objects.get(id=pk)

    definitions = term.definition_set.all()
    sentences = term.sentences.all()
    today = datetime.date.today()

    try:
        now = datetime.date.today()
        last = term.reviewed_at
        span = now - last
        days = span.days
        if days == 0:
            days = 'Hoy'
        elif days == 1:
            days = 'Ayer'
        else:
            days = 'Hace' + str(days) + 'días'
    except:
        days = None

    return render(request, 'es/term.html', {
        'term': term,
        'days': days,
        'definitions': definitions,
        'sentences': sentences,
        'today': today
    })


def term_add(request):
    form = TermForm(request.POST or None, files=request.FILES or None)
    context = {'form': form}

    if request.method == 'POST' and form.is_valid():
        term = form.save(commit=False)
        definition_formset = TermForm.DefinitionFormset(
            request.POST, instance=term)
        sentence_formset = TermForm.SentenceFormset(
            request.POST, files=request.FILES, instance=term)

        if definition_formset.is_valid() and sentence_formset.is_valid():

            term.save()

            definition_formset.save()
            sentence_formset.save()

            messages.success(
                request, 'Has añadido un nuevo termino 「{}」'.format(term.name))
            return redirect('es:index')
        else:
            context['definition_formset'] = definition_formset
            context['sentence_formset'] = sentence_formset

    else:
        context['definition_formset'] = TermForm.DefinitionFormset()
        context['sentence_formset'] = TermForm.SentenceFormset()

    return render(request, 'es/terms_add.html', context)


def usages(request):
    usages = Usage.objects.all()
    context = {
        'usages': usages,
    }
    return render(request, 'es/usages.html', context)


def usage(request, pk):
    usage = Usage.objects.get(id=pk)
    context = {
        'usage': usage,
    }
    return render(request, 'es/usage.html', context)


def search(request):

    if request.method == 'GET' and request.GET.get('q'):
        keyword = request.GET.get('q').strip()
        if keyword != '':

            q = Q(body__contains=keyword) | Q(term__name__contains=keyword)
            terms = Term.objects.filter(name__contains=keyword)
            sentences = Sentence.objects.filter(q)
            context = {
                'sentences': sentences,
                'terms': terms,
                'keyword': keyword
            }
            if sentences.count() == 0 and terms.count() == 0:
                messages.warning(
                    request, "No keyword matched")
            else:
                messages.info(
                    request, '{} términos y {} oración.'.format(terms.count(), sentences.count()))
        else:
            messages.error(
                request, "Please enter strings.")
            context = {}

        return render(request, 'es/search.html', context)
    else:
        messages.error(
            request, "Something went wrong with the search. Please try again.")
        return redirect('es:index')
