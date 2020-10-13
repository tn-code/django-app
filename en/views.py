import random
import datetime
import json
import sqlite3
import pandas as pd
from django_pandas.io import read_frame

from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models.functions import Lower
from django.forms.models import model_to_dict
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models.functions import Lower
from django.utils.html import format_html

from .forms import TermForm, SentenceForm, SynonymForm
from .models import Term, Comparison, Synonym, Definition, Sentence, Genre, Occasion, Derivative, Collocation, Usage, Grammar, Line, Dialogue


# def export_csv(request):
#    qs = Term.objects.all()
#    df = read_frame(qs, fieldnames=['name','type'])

def index(request):

    usages = Usage.objects.all()
    grammars = Grammar.objects.all()
    templates = Term.objects.filter(type='TEMPLATE')[:5]
    occasions = Occasion.objects.all()[:5]
    genres = Genre.objects.all()[:5]
    comparisons = Comparison.objects.all()[:5]
    today = datetime.date.today()
    todays = Term.objects.filter(created_at=today).exclude(
        Q(is_basic=True, is_advanced=False))

    try:
        todays_terms = todays
    except:
        todays_terms = None
    random_list = [item.id for item in Sentence.objects.all().exclude(
        image=None).order_by('?')]
    random.shuffle(random_list)
    if len(random_list) != 0:
        pickup_id = random_list[0]
        pickup = Sentence.objects.get(id=pickup_id)
    else:
        pickup = None
    count = Sentence.objects.all().exclude(image=None).count()

    total = Term.objects.all().count() - Term.objects.filter(type='TEMPLATE').count()
    Term.objects.filter(is_basic=True, is_advanced=False).count()

    context = {
        'usages': usages,
        'grammars': grammars,
        'comparisons': comparisons,
        'templates': templates,
        'occasions': occasions,
        'genres': genres,
        'todays': todays,
        'todays_terms': todays_terms,
        'total': total,
        'pickup': pickup,
        'count': count

    }
    return render(request, 'en/index.html', context)


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
                    request, '{} terms and {} sentences are found.'.format(terms.count(), sentences.count()))
        else:
            messages.error(
                request, "Please enter strings.")
            context = {}

        return render(request, 'en/search.html', context)
    else:
        messages.error(
            request, "Something went wrong with the search. Please try again.")
        return redirect('en:index')


def term(request, pk):
    term = Term.objects.get(id=pk)
    # TODO: Combine them with 'union' method
    # from_synonyms = term.synonyms.all()  # from_term
    to_synonyms = term.terms_related.all()  # to_term
    definition_instances = term.definition_set.all()
    sentences = term.sentences_related.all()
    today = datetime.date.today()
    derivatives = Derivative.objects.filter(base=term)
    base = Derivative.objects.filter(derivative=term).first()

    definition_list = []
    collocations = []
    for definition in definition_instances:
        id = definition.id
        definition_list.append(definition)

        collocation = Collocation.objects.filter(definition=id)
        if collocation:
            collocations.append(collocation)
        else:
            collocations.append(None)

    definitions = zip(definition_list, collocations)

    try:
        now = datetime.date.today()
        last = term.reviewed_at
        span = now - last
        days = span.days
        if days == 0:
            days = 'Today'
        elif days == 1:
            days = 'yesterday'
        else:
            days = str(days) + ' days ago'
    except:
        days = None

    return render(request, 'en/term.html', {
        'term': term,
        'days': days,
        'synonyms_ls': to_synonyms,
        'definitions': definitions,
        'sentences': sentences,
        'derivatives': derivatives,
        'base': base,
        'collocations': collocations,
        'today': today

    })


def lexicon(request):
    terms = {}
    phrases = {}
    phrasal_verbs = {}
    advanceds = {}
    basics = {}
    compounds = {}

    alphabets = list("abcdefghijklmnopqrstuvwxyz")

    for alpha in alphabets:
        word = Term.objects.filter(name__istartswith=alpha).filter(
            is_basic=False, type='WORD').order_by(Lower('name'))
        phrase = Term.objects.filter(name__istartswith=alpha).filter(
            type='PHRASE', is_basic=False).order_by(Lower('name'))
        phrasal_verb = Term.objects.filter(name__istartswith=alpha).filter(
            type='PHRASAL_VERB').order_by(Lower('name'))
        advanced = Term.objects.filter(name__istartswith=alpha).filter(
            is_basic=True, is_advanced=True).order_by(Lower('name'))
        basic = Term.objects.filter(name__istartswith=alpha).filter(
            is_basic=True, is_advanced=False).order_by(Lower('name'))
        compound = Term.objects.filter(name__istartswith=alpha).filter(
            type='COMPOUND').order_by(Lower('name'))
        terms[alpha] = word
        phrases[alpha] = phrase
        phrasal_verbs[alpha] = phrasal_verb
        advanceds[alpha] = advanced
        basics[alpha] = basic
        compounds[alpha] = compound

    count = {}
    lexicon = {
        'terms': terms,
        'phrases': phrases,
        'phrasal_verbs': phrasal_verbs,
        'advanceds': advanceds,
        'basics': basics,
        'compounds': compounds
    }
    for type, value in lexicon.items():
        # type dict
        sum = 0
        for key, item in value.items():
            sum += item.count()

        x = str(type)
        count[x] = sum

    loanwords = Term.objects.filter(
        type='LOANWORD').order_by(Lower('name'))
    symbols = ['1', '2', '3', '4', '5', '6', '7', '8', '9',
               '0', '-', '_', '～', '~', '(', ')', '[', ']', '.', ' ']

    templates = Term.objects.filter(type='TEMPLATE')

    context = {
        'terms': terms,
        'phrases': phrases,
        'phrasal_verbs': phrasal_verbs,
        'loanwords': loanwords,
        'compounds': compounds,
        'basics': basics,
        'advanceds': advanceds,
        'templates': templates,
        'count': count
    }
    return render(request, 'en/lexicon.html', context)


def terms(request):
    terms = Term.objects.filter(
        is_basic=False, type='WORD').order_by('name')

    context = {
        'terms': terms,
    }
    return render(request, 'en/terms.html', context)


def occasions(request):
    occasions = Occasion.objects.all().order_by('name')
    context = {
        'occasions': occasions,
    }
    return render(request, 'en/occasions.html', context)


def occasion(request, pk):
    occasion = Occasion.objects.get(id=pk)
    terms = occasion.terms.all()
    sentences = occasion.sentences.all()
    dialogues = occasion.dialogue_set.all()

    context = {
        'occasion': occasion,
        'terms': terms,
        'generics': sentences,
        'dialogues': dialogues
    }
    return render(request, 'en/occasion.html', context)


def comparisons(request):
    comparisons = Comparison.objects.all()
    return render(request, 'en/comparisons.html', {'comparisons': comparisons})


def comparison(request, pk):
    comparison = Comparison.objects.get(id=pk)
    return render(request, 'en/comparison.html', {'comparison': comparison})


def templates(request):
    templates = Term.objects.filter(type='TEMPLATE').order_by('name')
    context = {
        'templates': templates,
    }
    return render(request, 'en/templates.html', context)


def template(request, pk):
    template = Term.objects.get(id=pk)
    sentences = template.sentences_related.all()
    templates = Term.objects.filter(type='TEMPLATE')

    def get_next_template(id):
        id += 1
        if templates.get(id=id):
            return templates.get(id=id)
        else:
            get_next_template(id)

    def get_prev_template(id):
        id -= 1
        if templates.get(id=id):
            return templates.get(id=id)
        else:
            get_next_template(id)
    try:
        next = get_next_template(pk)
    except:
        next = None
    try:
        prev = get_prev_template(pk)
    except:
        prev = None

    context = {
        'template': template,
        'sentences': sentences,
        'next': next,
        'prev': prev
    }
    return render(request, 'en/template.html', context)


def genres(request):
    genres = Genre.objects.all().order_by('name')
    context = {
        'genres': genres,
    }
    return render(request, 'en/genres.html', context)


def genre(request, pk):
    genre = Genre.objects.get(id=pk)
    terms = genre.terms.all()
    context = {
        'genre': genre,
        'terms': terms
    }
    return render(request, 'en/genre.html', context)


def grammars(request):
    return render(request, 'en/grammars.html', {
    })


def paraphrase(request):
    basics = Term.objects.filter(is_basic=True)
    return render(request, 'en/paraphrase.html', {
        'basics': basics
    })


def terms_add(request):
    form = TermForm(request.POST or None, files=request.FILES or None)
    context = {'form': form}
    context['synonyms'] = Term.objects.all().order_by(Lower('name'))
    context['genres'] = Genre.objects.all().order_by(Lower('name'))
    context['occasions'] = Occasion.objects.all().order_by(Lower('name'))
    if request.method == 'POST' and form.is_valid():
        term = form.save(commit=False)
        definition_formset = TermForm.DefinitionFormset(
            request.POST, instance=term)
        sentence_formset = TermForm.SentenceFormset(
            request.POST, files=request.FILES, instance=term)
        derivative_formset = TermForm.DerivativeFormset(
            request.POST, files=request.FILES, instance=term)
        synonym_formset = TermForm.SynonymFormset(
            request.POST, files=request.FILES, instance=term)

        if definition_formset.is_valid() and sentence_formset.is_valid() and derivative_formset.is_valid():

            term.save()
            # FIXME: To_synonym selected is nothing but random.
            try:
                to_synonym = Term.objects.get(
                    id=request.POST.get('synonym_pks'))
                term.synonyms.add(to_synonym)
            except:
                pass
            try:
                genre = Genre.objects.get(id=request.POST.get('genre_pk'))
                term.genres.add(genre)
            except:
                pass
            try:
                occasion = Occasion.objects.get(
                    id=request.POST.get('occasion_pk'))
                term.occasions.add(occasion)
            except:
                pass

            definition_formset.save()
            sentence_formset.save()
            derivative_formset.save()
            synonym_formset.save()

            messages.success(
                request, 'New term 「{}」has been added successfully'.format(term.name))
            return redirect('en:index')
        else:
            context['definition_formset'] = definition_formset
            context['sentence_formset'] = sentence_formset
            context['derivative_formset'] = derivative_formset
            context['synonym_formset'] = synonym_formset

    else:
        context['definition_formset'] = TermForm.DefinitionFormset()
        context['sentence_formset'] = TermForm.SentenceFormset()
        context['collocation_formset'] = TermForm.CollocationFormset()
        context['derivative_formset'] = TermForm.DerivativeFormset()
        context['synonym_formset'] = TermForm.SynonymFormset()

    return render(request, 'en/terms_add.html', context)


def synonym_add(request):
    form = SynonymForm(request.POST or None)
    context = {'form': form}
    if request.method == 'POST' and form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(
            request, "「{0}」 and 「{1}」 are successfully marked as synonyms".format(instance.from_term.name, instance.to_term.name))
        return redirect('en:index')
    else:
        pass

    return render(request, 'en/synonym_add.html', context)


def sentences(request):
    pass


def sentence_add(request):
    form = SentenceForm(request.POST or None, files=request.FILES or None)
    context = {'form': form}
    if request.method == 'POST' and form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        if instance.is_generic == False:
            messages.success(
                request, format_html(
                    "New sentence has been successfully added to the term 「<a class='link-message' href='/en/terms/{}'>{}</a>」", instance.term.id, instance.term.name)
            )
        else:
            messages.success(
                request, format_html(
                    "New generic sentence (<a class='link-message' href='http://127.0.0.1:8000/admin/en/sentence/{}/change/'>ID:{}</a>) has been successfully added.", instance.id, instance.id)
            )
        return redirect('en:index')
    else:
        pass

    return render(request, 'en/sentence_add.html', context)


def comparison_add(request):
    pass


def term_review(request, pk):
    term = get_object_or_404(Term, id=pk)
    term.reviewed_at = datetime.date.today()
    term.save(update_fields=["reviewed_at"])
    return redirect('en:term', pk=term.id)


def terms_edit(request, pk):
    term = get_object_or_404(Term, id=pk)

    if request.method == 'POST':
        form = form = TermForm(request.POST, files=request.FILES)
        if form.is_valid():
            term.save()
            return redirect('/en/terms')
    else:
        form = TermForm(initial=model_to_dict(term))
        context = {'form': form}
        context['genres'] = Genre.objects.all().order_by('name')
        context['occasions'] = Occasion.objects.all().order_by('name')

        return render(request, 'en/terms_edit.html', context)


# USAGES

def usages(request):
    usages = Usage.objects.all()
    books = Usage.objects.all()
    websites = Usage.objects.filter(source_media='WEBSITE')
    context = {
        'usages': usages,
        'books': books,
        'websites': websites
    }
    return render(request, 'en/usages.html', context)


def usage(request, pk):
    usage = Usage.objects.get(id=pk)
    context = {
        'usage': usage,
    }
    return render(request, 'en/usage.html', context)

# QUIZZES


def json_serial(obj):
    # Convert Date type to strings as it's not supported in JSON
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s is not serializable" % type(obj))


def create_basic_quiz(term):

    term['question'] = 'Select a word that matches to the definition(s) below.'

    # adding the first definition
    definitions, sentences = \
        Definition.objects.filter(term=term['id']).values(), \
        Sentence.objects.filter(term=term['id']).values()

    definition_list = [d['definition'] for d in definitions]
    sentence_list = [s for s in sentences]

    random.shuffle(definition_list)
    random.shuffle(sentence_list)

    term['definitions'] = definition_list
    term['sentences'] = sentence_list

    # Creating choices

    query = Q(is_basic=False) | (Q(is_basic=True) and Q(is_advanced=True))

    id_list = Term.objects.filter(query).values_list('id', flat=True)

    random_ids = [random.choice(id_list) for i in range(0, 3)]
    choices = [Term.objects.get(id=id).name
               for id in random_ids if Term.objects.get(id=id)]
    choices.append(term['name'])

    random.shuffle(choices)
    term['choices'] = choices

    term['type'] = 'basic'
    term['answer'] = term['name']

    return term


def create_sentence_quiz(term):

    term['question'] = 'Select a word that matches to the sentence below.'

    sentences = Sentence.objects.filter(
        term=term['id']).values()

    sentence_list = [s for s in sentences]
    random.shuffle(sentence_list)
    term['sentences'] = sentence_list

    # adding the first definition

    definitions = Definition.objects.filter(
        term=term['id']).values()
    definition_list = [d['definition'] for d in definitions]
    term['definitions'] = definition_list

    # Creating choices
    choices = []
    query = Q(is_basic=False) | (Q(is_basic=True) and Q(is_advanced=True))
    id_list = []
    id_list = Term.objects.filter(query).values_list('id', flat=True)
    choices.append(term['name'])
    for i in range(0, 3):
        random_id = random.choice(id_list)
        if Term.objects.get(id=random_id):
            choices.append(Term.objects.get(id=random_id).name)
        else:
            pass

    random.shuffle(choices)
    term['choices'] = choices
    term['type'] = 'sentence'

    term['answer'] = term['name']

    return term


def synonym_quizzes(terms, num):
    term['question'] = "Fill out the sentence below with its definition(s) shown."
    definitions = Definition.objects.filter(
        term=term['id']).values()

    definition_list = []
    for definition in definitions:
        definition_list.append(definition['definition'])
    term['definitions'] = definition_list

    sentence_list = []
    sentences = Sentence.objects.filter(term=term['id']).values()
    for sentence in sentences:
        temp = {}
        temp['body'] = sentence['body']
        temp['image'] = sentence['image']
        temp['source_name'] = sentence['source_name']
        temp['source_link'] = sentence['source_link']
        temp['source_media'] = sentence['source_media']
        sentence_list.append(temp)

    term['sentence'] = sentence_list
    term['answer'] = term['name']


def create_quizzes(terms, num):
    quizzes = []
    count = 0

    # Take out one dict that represents one Term instance
    for term in terms:
        instance = Term.objects.get(id=term['id'])
        if count < num:
            if instance.sentences_related.count() > 0 and random.randint(0, 100) > 70:
                term = create_sentence_quiz(term)
                term['point'] = 1
            else:
                term = create_basic_quiz(term)
                term['point'] = 1
            # Pass the dict to templates as it is as the foreign keys and m2m object that contains term object causing json parse error
            term['id'] = instance.id
            quizzes.append(term)
            count += 1
        else:
            pass

    return quizzes


def quizzes(request):
    # 'values' make a list of dictionaries in which each represents one instance of the model. [{1:foo}, {2:bar}...]
    query = Q(is_basic=False) | (Q(is_basic=True) and Q(is_advanced=True))
    terms = Term.objects.filter(query).order_by('?').values(
        'id', 'name', 'is_basic', 'is_advanced')

    items = create_quizzes(terms, 100)

    context = {}

    context['terms'] = items  # Only for checking values in Django template
    context["items"] = json.dumps(
        items, default=json_serial)  # For Vue.js variables

    return render(request, 'en/quizzes.html', context)


def update_quiz(request):
    if request.method == 'POST' and request.body:
        json_dict = json.loads(request.body)
        pk = json_dict['id']
        point = json_dict['point']

        term = get_object_or_404(Term, id=pk)
        term.reviewed_at = datetime.date.today()
        term.proficiency += point
        term.save(update_fields=["reviewed_at", "proficiency"])
        return JsonResponse(json_dict)
    else:
        return HttpResponseServerError()
