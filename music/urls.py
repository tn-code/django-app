from django.contrib import admin
from django.urls import path
from .views import index, artists, artist, get_svg, spotify_json, plot_track_chart, tracks, track, usage, usages, chords, chord, instrument, instruments, charts, composition
urlpatterns = [
    path('', index, name="index"),
    path('charts/', charts, name="charts"),
    path('composition/', composition, name="composition"),
    path('artists/', artists, name="artists"),
    path('artists/<int:pk>/', artist, name="artist"),
    path('tracks/', tracks, name="tracks"),
    path('tracks/<int:pk>/', track, name="track"),
    path('chords/', chords, name="chords"),
    path('chords/<int:pk>/', chord, name="chord"),
    path('instruments/', instruments, name="instruments"),
    path('instruments/<int:pk>', instrument, name="instrument"),
    path('composition/usages/', usages, name="usages"),
    path('composition/usages/<int:pk>', usage, name="usage"),
    path('spotify_json/', spotify_json, name="spotify_json"),
    path('plot/', get_svg, name="plot"),
    path('plots/tracks/<int:pk>/', plot_track_chart, name="track_plot")
]
