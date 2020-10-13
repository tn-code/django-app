from django.contrib import admin
from django.urls import path
from .views import index, medicines, medicine, ingredients, ingredient, terms, term, documents, property, precautions, precaution, clients, client, symptom, symptoms, laws, law, article, effects, effect, properties, category, kanpo

urlpatterns = [
    path('', index, name="index"),
    path('medicines/', medicines, name="medicines"),
    path('medicines/<int:pk>', medicine, name="medicine"),
    path('medicine/caterogy/<int:pk>', category, name="category"),
    path('ingredients/', ingredients, name="ingredients"),
    path('ingredients/<int:pk>', ingredient, name="ingredient"),
    path('kanpo', kanpo, name="kanpo"),
    path('effects/', effects, name="effects"),
    path('effects/<int:pk>', effect, name='effect'),
    path('terms/', terms, name="terms"),
    path('terms/<int:pk>', term, name="term"),
    path('symptoms/', symptoms, name="symptoms"),
    path('symptoms/<int:pk>', symptom, name="symptom"),
    path('laws/', laws, name="laws"),
    path('laws/<int:pk>', law, name="law"),
    path('laws/<int:pk>/articles/<int:id>', article, name="article"),
    path('documents/', documents, name="documents"),
    path('properties/', properties, name="properties"),
    path('properties/<int:pk>', property, name="property"),
    path('precautions', precautions, name="precautions"),
    path('precautions/<int:pk>', precaution, name="precaution"),
    path('clients', clients, name="clients"),
    path('clients/<int:pk>', client, name="client")
]
