from django.contrib import admin
from django.urls import path
from .views import index, exhibitions, exhibition, works, work, artists, artist, genres, genre, designs, design, museums, museum

urlpatterns = [
    path('', index, name="index"),
    path('exhibitions/', exhibitions, name="exhibitions"),
    path('exhibitions/<int:pk>', exhibition, name="exhibition"),
    path('works/', works, name="works"),
    path('works/<int:id>/', work, name="work"),
    path('artists', artists, name="artists"),
    path('artists/<int:id>', artist, name="artist"),
    path('genres/', genres, name="genres"),
    path('genres/<int:id>', genre, name="genre"),
    path('designs/', designs, name="designs"),
    path('designs/<int:pk>', design, name="design"),
    path('museums/', museums, name="museums"),
    path('museums/<int:pk>', museum, name="museum")
]
