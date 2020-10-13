from django.contrib import admin
from django.urls import path
from .views import index, book, quotes, themes, theme, memos, books, get_svg, ThemeCreate, quote, book_add, category

urlpatterns = [
    path('', index),
    path('books/', books, name="books"),
    path('category/<int:pk>', category, name="category"),
    path('books/<int:pk>', book, name="book"),
    path('books/add', book_add, name="book_add"),
    path('quotes/', quotes, name="quotes"),
    path('quotes/<int:id>', quote, name="quote"),
    path('themes/', themes, name="themes"),
    path('themes/<int:id>/', theme, name="theme"),
    path('themes/add/', ThemeCreate.as_view(success_url="/lib/themes/")),
    path('memos/', memos, name="memos"),
    path('books/plot', get_svg, name="plot")
]
