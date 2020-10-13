from datetime import date

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.db.models import Q
import random

from .models import Medicine, Ingredient, Effect, Term, Document, Property, Client, Precaution, MedicineImage, Symptom, SymptomImage, TermImage, Law, Article, Category


def index(request):
    return render(request, 'pharmacy/index.html')


def medicine(request, pk):
    medicine = Medicine.objects.get(id=pk)
    medicine_images = MedicineImage.objects.filter(
        medicine=pk).order_by('created_at')
    related_medicines = medicine.related_medicines.all()
    context = {
        'medicine': medicine,
        'medicine_images': medicine_images,
        'related_medicines': related_medicines,
    }
    return render(request, 'pharmacy/medicine.html', context)


def medicines(request):
    medicines = Medicine.objects.all()
    categories = Category.objects.all()
    context = {
        'medicines': medicines,
        'categories': categories
    }
    return render(request, 'pharmacy/medicines.html', context)


def kanpo(request):
    kanpoes = Ingredient.objects.filter(properties__in=[20])
    ingredients = Ingredient.objects.filter(properties__in=[7])

    context = {
        'kanpoes': kanpoes,
        'ingredients': ingredients
    }

    return render(request, 'pharmacy/kanpo.html', context)


def category(request, pk):
    medicines = Medicine.objects.order_by('name').filter(category=pk)
    categories = Category.objects.all()
    category = Category.objects.get(id=pk)
    ingredient_list = []
    ingredient_pk = []

    for medicine in medicines:
        for ingredient in medicine.ingredients.all():
            if ingredient.id in ingredient_pk:
                pass
            else:
                ingredient_pk.append(ingredient.id)
                ingredient_list.append(ingredient)
    random.shuffle(ingredient_list)
    context = {
        'medicines': medicines,
        'category': category,
        'categories': categories,
        'ingredients': ingredient_list
    }
    return render(request, 'pharmacy/categories.html', context)


def ingredients(request):
    ingredients = Ingredient.objects.order_by('name').all()
    context = {
        'ingredients': ingredients
    }
    return render(request, 'pharmacy/ingredients.html', context)


def ingredient(request, pk):
    ingredient = Ingredient.objects.get(id=pk)
    prohibitions = ingredient.precautions.filter(type="PROHIBITION")
    consultations = ingredient.precautions.filter(type="CONSULTATION")
    precautions = ingredient.precautions.filter(type="PRECAUTION")
    related_ingredients = ingredient.related_ingredients.all()

    context = {
        'ingredient': ingredient,
        'prohibitions': prohibitions,
        'consultations': consultations,
        'precautions': precautions,
        'related_ingredients': related_ingredients
    }
    return render(request, 'pharmacy/ingredient.html', context)


def terms(request):

    def recursiveTree(term, parent_dict, level):
        level += 1
        if term.child_terms.count() > 0:
            parent_dict['children'] = []

            for child in term.child_terms.all():
                child_dict = {'level': level, 'children': []}
                child_dict['content'] = child
                parent_dict['children'].append(child_dict)
                recursiveTree(child, child_dict, level)

        else:
            pass

        return parent_dict

    terms = Term.objects.filter(parent=None)

    term_list = []
    for term in terms:
        init_dict = {'level': 0, 'content': term}
        term_tree = recursiveTree(term, init_dict, 0)
        term_list.append(term_tree)

    context = {
        'terms': term_list

    }
    return render(request, 'pharmacy/terms.html', context)


def term(request, pk):
    term = Term.objects.get(id=pk)
    context = {
        'term': term

    }
    return render(request, 'pharmacy/term.html', context)


def symptoms(request):
    symptoms = Symptom.objects.all()
    context = {
        'symptoms': symptoms

    }
    return render(request, 'pharmacy/symptoms.html', context)


def symptom(request, pk):
    symptom = Symptom.objects.get(id=pk)
    images = symptom.symptom_images.all()
    ingredients = symptom.ingredients.all()
    context = {
        'symptom': symptom,
        'images': images,
        'ingredients': ingredients

    }
    return render(request, 'pharmacy/symptom.html', context)


def laws(request):
    laws = Law.objects.all()
    context = {
        'laws': laws

    }
    return render(request, 'pharmacy/laws.html', context)


def law(request, pk):
    law = Law.objects.get(id=pk)
    articles = Article.objects.filter(law=law.id)
    context = {
        'law': law,
        'articles': articles

    }
    return render(request, 'pharmacy/law.html', context)


def article(request, pk, id):
    article = Article.objects.get(id=id)
    context = {
        'article': article

    }
    return render(request, 'pharmacy/article.html', context)


def documents(request):
    documents = Document.objects.all()
    context = {
        'documents': documents
    }
    return render(request, 'pharmacy/documents.html', context)


def properties(request):
    properties = Property.objects.all()

    context = {
        'properties': properties,
    }
    return render(request, 'pharmacy/properties.html', context)


def property(request, pk):
    property = Property.objects.get(id=pk)
    ingredients = property.ingredients.all()

    context = {
        'property': property,
        'ingredients': ingredients
    }

    if pk == 20:
        p = Property.objects.get(id=7)
        compositions = Ingredient.objects.filter(id__in=[20, 31, 49])
        others = p.ingredients.all().exclude(id__in=[20, 31, 49])
        compositions.union(others)
        contents = []
        headers = ['NAME']

        for composition in compositions:
            headers.append(composition.name)

        headers.append('stamina')
        headers.append('status')

        for ingredient in ingredients:
            key = ingredient.name

            temp = {}
            temp[key] = []

            for composition in compositions:
                if composition in ingredient.relationships.all():
                    temp[key].append(True)
                else:
                    temp[key].append(False)
            temp[key].append(ingredient.stamina)
            temp[key].append(ingredient.target)

            contents.append(temp)

        context['titles'] = headers
        context['contents'] = contents

        return render(request, 'pharmacy/tcm.html', context)
    else:
        return render(request, 'pharmacy/property.html', context)


def precautions(request):
    prohibitions = Ingredient.precautions.filter(type="PROHIBITION")
    consultations = Ingredient.precautions.filter(type="CONSULTATION")
    precautions = Ingredient.precautions.filter(type="PRECAUTION")

    context = {
        'prohibitions': prohibitions,
        'consultations': consultations,
        'precautions': precautions
    }
    return render(request, 'pharmacy/precautions.html', context)


def clients(request):
    pass


def client(request, pk):
    client = Client.objects.get(id=pk)
    guidelines = Precaution.objects.filter(client=client)
    prohibitions = guidelines.filter(type="PROHIBITION")
    consultations = guidelines.filter(type="CONSULTATION")
    precautions = guidelines.filter(type="PRECAUTION")

    context = {
        'client': client,
        'prohibitions': prohibitions,
        'consultations': consultations,
        'precautions': precautions
    }
    return render(request, 'pharmacy/client.html', context)


def effects(request):
    effects = Effect.objects.all()

    context = {
        'effects': effects,
    }
    return render(request, 'pharmacy/effects.html', context)


def effect(request, pk):
    effect = Effect.objects.get(id=pk)
    ingredients = effect.ingredients.all()

    context = {
        'effect': effect,
        'ingredients': ingredients
    }
    return render(request, 'pharmacy/effect.html', context)


def precaution(request, pk):
    precaution = Precaution.objects.get(id=pk)
    context = {
        'precaution': precaution

    }
    return render(request, 'pharmacy/precaution.html', context)
