from django.contrib import admin
from django.urls import path, include
from .views import index, terms, term, comparisons, comparison, grammars, paraphrase, terms_add, terms_edit, term_review, occasion, occasions, sentences, sentence_add, quizzes, synonym_add, templates, template, genres, genre, lexicon, update_quiz, usages, usage, search

quiz_patterns = ([
    path('', quizzes, name='quizzes'),
    path('update/success', update_quiz, name='update_quiz_success')
])


urlpatterns = [
    path('', index, name="index"),
    path('lexicon/', lexicon, name="lexicon"),
    path('search', search, name="search"),
    path('terms/', terms, name="terms"),
    path('terms/<int:pk>', term, name="term"),
    path('terms/add', terms_add, name="term_add"),
    path('terms/<int:pk>/edit', terms_edit, name="edit_term"),
    path('terms/<int:pk>/review', term_review, name="term_review"),
    path('synonyms/add', synonym_add, name="synonym_add"),
    path('sentences/', sentences, name="sentences"),
    path('sentences/add', sentence_add, name="sentence_add"),
    path('comparisons/', comparisons, name="comparisons"),
    path('comparisons/<int:pk>', comparison, name="comparison"),
    path('grammars/', grammars, name="grammars"),
    path('paraphrase/', paraphrase, name="paraphrase"),
    path('occasions/', occasions, name="occasions"),
    path('occasions/<int:pk>', occasion, name="occasion"),
    path('templates/', templates, name="templates"),
    path('templates/<int:pk>/', template, name="template"),
    path('genres/', genres, name="genres"),
    path('genres/<int:pk>/', genre, name="genre"),
    path('usages/', usages, name="usages"),
    path('usages/<int:pk>', usage, name="usage"),
    path('quizzes/', include(quiz_patterns)),
]
