import datetime
import time
import urllib.request
import urllib.error
import math
import collections
import io
import numpy as np
from datetime import date
import statistics
from threading import RLock

try:
    import matplotlib
    matplotlib.use('Agg')
finally:
    from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib import colors

from django.db.models import Q
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse

import spotipy
import spotipy.util as util

from .models import Artist, Track, Chart, Progression, Tip, TipImage, TipCategory, Instrument

# Prevent unnecessary token expired error
if cache.ttl('reset_track_chart') == 0 or cache.ttl('reset_artist_chart') == 0:
    scope = 'user-top-read playlist-modify-private playlist-read-private'
    user = settings.SPOTIFY_USERNAME
    token = util.prompt_for_user_token(settings.SPOTIFY_USERNAME,
                                       scope,
                                       client_id=settings.SPOTIFY_CLIENT_ID,
                                       client_secret=settings.  SPOTIFY_CLIENT_SECRET,
                                       redirect_uri='http://127.0.0.1:8000/')
    sp = spotipy.Spotify(auth=token)
else:
    pass

contents = {}


def sec_to_datetime(sec):
    days = sec / (24 * 60 * 60)
    hours = (days - math.floor(days)) * 24
    minutes = (hours - math.floor(hours)) * 60
    seconds = math.floor((minutes - math.floor(minutes)) * 60)

    time = ""
    if minutes >= 1:
        time = str(math.floor(minutes)) + ' min ' + time
    if hours >= 1:
        time = str(math.floor(hours)) + ' hrs ' + time
    if days >= 1:
        time = str(math.floor(days)) + ' days ' + time

    return time


def check_online():
    # check internet connection by trying accessing to google search page.
    try:
        urllib.request.urlopen('http://216.58.192.142', timeout=1)
        return True
    except urllib.error.URLError as err:
        return False


def save_track_chart_data(tracks):
    rank_count = 1

    for track in tracks['items']:
        # Get existing track or create new track data

        try:
            t = Track.objects.get(name__exact=track['name'])
        except:
            t = Track(name=track['name'])
            t.save()

        # Get existing artist or create new artist data
        for artist in track['artists']:
            try:
                a = Artist.objects.get(name__exact=artist['name'])
            except:
                a = Artist(name=artist['name'], spotify_id=artist['id'])
                a.save()
            finally:
                # Append the artist to the track object
                t.artists.add(a)

        # Create new chart object with track name
        chart = Chart(track=t, rank=rank_count)
        chart.save()

        # Note that a song chart object only has a track that contains  mutiple artists data within it.
        rank_count += 1


def save_artist_chart_data(artists):
    rank_count = 1

    # Get existing artist or create new artist data
    for artist in artists['items']:
        try:
            a = Artist.objects.get(name__exact=artist['name'])
        except:
            a = Artist(name=artist['name'], spotify_id=artist['id'])
            a.save()

        chart = Chart(artist=a, rank=rank_count)
        chart.save()

        rank_count += 1


def calc_cache_expiration():
    dt = datetime.datetime.now()
    # Reset span in days for artist chart
    reset_span = 6
    # Reset span in days for track chart
    track_reset_span = 0
    # Reset time in hours
    reset_time = 6

    hour_sec = int(dt.hour) * 60 * 60
    minute_sec = int(dt.minute) * 60
    reset_sec = reset_time * 60 * 60
    span_sec = reset_span * 24 * 60 * 60
    track_reset_span_sec = track_reset_span * 24 * 60 * 60

    # Work out remaining time to reset caches in order to flush db at certain times.

    # If current time in range of 0:00 - reset time
    if int(dt.hour) in range(0, reset_time):
        reset_ttl = reset_sec - (hour_sec + minute_sec)
    # When current time in range of reset time - 23:59
    else:
        reset_ttl = ((24 * 60 * 60) - (hour_sec + minute_sec)) + reset_sec

    expire_ttl = {
        'reset_ttl': reset_ttl,
        'span_sec': span_sec,
        'reset_span': reset_span
    }

    return expire_ttl


def clean_track_data(tracks):
    items = []
    for track in tracks:
        artists = []
        for artist in track['artists']:
            artists.append(artist['name'])

        # pk = Track.objects.get(spotify_id=track['id'])

        track = {
            # 'id':pk,
            'spotify_id': track['id'],
            'name': track['name'],
            'image': track['album']['images'][0],
            'artists': artists,
            'date': track['album']['release_date'],
            'album': track['album']['name']
        }

        items.append(track)

    return items


def clean_artist_data(artists):
    items = []
    for artist in artists:
        instance = Artist.objects.get(spotify_id=artist['id'])
        pk = instance.id
        # Existing value in key 'id', which is given by Spotify, is now replaced with Artist instance primary key in order not to collid with each other referencing the same key
        artist = {
            'id': pk,
            'spotify_id': artist['id'],
            'name': artist['name'],
            'image': artist['images'][0],
            'genres': artist['genres'],
            'followers': artist['followers']['total']
        }
        items.append(artist)

    return items


def add_artist_position(artists, days):
    items = []

    dt = datetime.date.today()
    # Note that reset span(days) 0 means next morning.
    last_date = (datetime.datetime.now() -
                 datetime.timedelta(int(days)+1)).strftime('%Y-%m-%d')

    # Get the latest charts and the last charts
    # MEMO: 'charts' are sets of Chart objects, which is an intermediate table, that respectively have only one track-artist data.
    new_charts = Chart.objects.filter(date=dt).exclude(artist=None)
    last_charts = Chart.objects.filter(date=last_date).exclude(artist=None)

    # Create a list of artists(dict) in the last chart
    last_artists = []
    for chart in last_charts:
        last_artists.append(chart.artist)

    positions = []
    # Check position of tracks one by one
    for chart in new_charts:
        artist = chart.artist

        # The artist found in the last chart
        if artist in last_artists:
            # This case requires to get 2 chart objects, a new chart and a last_chart, to compare their ranks.
            try:
                last_chart = Chart.objects.get(artist=artist, date=last_date)
            except:
                error = 'No track with a name attribute" ' + \
                    artist.name + ' " found in the last chart.'
                return redirect('music:index')

            new_rank = chart.rank
            last_rank = last_chart.rank

            # Compare the two ranks to set a position
            if new_rank < last_rank:
                position = 'UP'
            elif new_rank > last_rank:
                position = 'DOWN'
            elif new_rank == last_rank:
                position = 'EQUAL'
            else:
                position = 'UNKNOWN'

        # The track not found in the "LAST" chart
        else:
            # Check if the track ranks in for the first time or comes back again after some out-of-chart time
            # Make sure to exclude the latest chart since it's already saved in the database
            if Chart.objects.filter(artist=artist).count() > 1:
                position = 'BACK'
            else:
                position = 'NEW'

        positions.append(position)

    index = 0
    for artist in artists:
        artist['position'] = positions[index]
        items.append(artist)
        index += 1

    return items


def add_track_position(tracks, days):

    items = []

    dt = datetime.date.today()
    # Note that reset span(days) 0 means next morning.
    last_date = (datetime.datetime.now() -
                 datetime.timedelta(int(days) + 1)).strftime('%Y-%m-%d')

    # Get the latest charts and the last charts
    # MEMO: 'charts' are sets of Chart objects, which is an intermediate table, that respectively have only one track-artist data.
    new_charts = Chart.objects.filter(date=dt).exclude(track=None)
    last_charts = Chart.objects.filter(date=last_date).exclude(track=None)

    # Create a list of tracks(dict) in the last chart
    last_tracks = []
    for chart in last_charts:
        last_tracks.append(chart.track)

    positions = []
    # Check position of tracks one by one
    for chart in new_charts:
        track = chart.track

        # The track found in the last chart
        if track in last_tracks:
            # This case requires to get 2 chart objects, a new chart and a last_chart, to compare their ranks.
            try:
                last_chart = Chart.objects.get(track=track, date=last_date)
            except:
                error = 'No track with a name attribute" ' + \
                    track.name + ' " found in the last chart.'
                return redirect('music:index')

            new_rank = chart.rank
            last_rank = last_chart.rank

            # Compare the two ranks to set a position
            # Be wary that higher rank is numerically lower
            diff = new_rank - last_rank
            if diff < 0:
                position = 'UP'
            elif diff > 0:
                position = 'DOWN'
            elif diff == 0:
                position = 'EQUAL'
            else:
                position = 'UNKNOWN'

        # The track not found in the "LAST" chart
        else:
            # Check if the track ranks in for the first time or comes back again after some out-of-chart time
            # Make sure to exclude the latest chart since it's already saved in the database
            if Chart.objects.filter(track=track).count() > 1:
                position = 'BACK'
            else:
                position = 'NEW'

        positions.append(position)

    index = 0
    for track in tracks:
        track['position'] = positions[index]
        items.append(track)
        index += 1

    return items


def fetch_spotify_data(request):
    # messages.success(
    #    request, 'Fetching new data due to all or some caches #expired. Make sure that at least one of the charts has been #updated.')
    # Calculate track reset time (Not to be set yet)
    expire_ttl = calc_cache_expiration()
    reset_span = expire_ttl['reset_span']

    if cache.ttl('reset_track_chart') == 0:
        res = sp.current_user_top_tracks(
            limit=50, offset=0, time_range='short_term')

        # Save data into database when no track reset cache exist.
        # MEMO: Pass the original data as an argument to ensure that original data goes to DB and cleaned data with positions for templates so that any further modifications in functions with cleaned data doesn't affect DB manipulations and its values.
        save_track_chart_data(res)

        # Clean track data
        cleaned_data = clean_track_data(res['items'])

        # Adding track positions
        # MEMO: Positions will only be cached without any database population
        contents['top_tracks'] = add_track_position(cleaned_data, 0)

        # Override the existing cache as it won't be expired.
        cache.set('top_tracks',
                  contents['top_tracks'], timeout=None)

        # Set new reset cache
        track_reset_ttl = expire_ttl['reset_ttl']
        cache.set("reset_track_chart", True, timeout=track_reset_ttl)

        messages.success(
            request, 'Top 10 tracks chart has been now updated.')
    else:
        contents['top_tracks'] = cache.get('top_tracks')
        # messages.info(
        #    request, 'Top tracks chart has not been updated.')

    if cache.ttl('reset_artist_chart') == 0:
        res = sp.current_user_top_artists(
            limit=10, offset=0, time_range='short_term')

        # Save data into database
        save_artist_chart_data(res)

        # Clean artist data
        cleaned_data = clean_artist_data(res['items'])

        # Adding track positions
        # MEMO: Positions will only be cached without any database population
        contents['top_artists'] = add_artist_position(cleaned_data, reset_span)

        # Override the existing cache as it won't be expired.
        cache.set('top_artists',
                  contents['top_artists'], timeout=None)

        # Set new reset cache
        artist_reset_ttl = expire_ttl['reset_ttl'] + expire_ttl['span_sec']
        cache.set("reset_artist_chart", True, timeout=artist_reset_ttl)

        messages.success(
            request, 'Top 10 artist chart has been now updated.')
    else:
        contents['top_artists'] = cache.get('top_artists')
        # messages.info(
        #    request, 'Top artist chart has not been updated.')

    return request


def index(request):
    context = {}
    return render(request, 'music/index.html', context)


def composition(request):
    context = {}
    return render(request, 'music/composition.html', context)


def charts(request):
    context = {}

    # Check if all the caches exist
    if cache.ttl('reset_track_chart') and cache.ttl('reset_artist_chart'):
        contents['top_artists'] = cache.get('top_artists')
        contents['top_tracks'] = cache.get('top_tracks')
        is_cached = True
        is_online = check_online()
        reset_ttl = cache.ttl('reset_track_chart')
        #
        # messages.success(
        #    request, 'Great! All Caches Exist!')
    # If caches doesn't exist (including the first access after certain reset times)
    else:
        # Check the internet connection in order to fetch data
        if check_online() == False:
            is_online = False
            messages.info(
                request, 'Unable to display contents due to no existance of caches and internet connection')
            return render(request, 'music/charts.html')
        # Fetching data online
        else:
            is_cached = False
            is_online = True

            fetch_spotify_data(request)

    reset_ttl = sec_to_datetime(cache.ttl('reset_track_chart'))
    reset_ttl2 = sec_to_datetime(cache.ttl('reset_artist_chart'))
    new_tracks = []
    for track in contents['top_tracks']:
        if track['position'] == 'NEW':
            new_tracks.append(track)
        else:
            pass

    countries = []
    for artist in Artist.objects.all().exclude(category__in=[1, 2]):
        try:
            if artist.country:
                countries.append(artist.country)
        except:
            pass
    country_dict = collections.Counter(countries)
    # Convert dict to list that contains keys(country names)
    country_list = list(country_dict)
    country_count = len(country_list)
    track_count = Track.objects.all().count()
    artist_count = Artist.objects.all().exclude(category__in=[1, 2]).count()

    context.update({
        'top_artists': contents['top_artists'],
        'top_tracks': contents['top_tracks'],
        'new_tracks': new_tracks,
        'is_online': is_online,
        'is_cached': is_cached,
        'reset_ttl': reset_ttl,
        'reset_ttl2': reset_ttl2,
        'country_count': country_count,
        'track_count': track_count,
        'artist_count': artist_count
    })
    return render(request, 'music/charts.html', context)


def artists(request):
    context = {}
    artists = {}
    crown_tracks = []
    crown_artists = []

    for chart in Chart.objects.filter(rank=1).exclude(track=None):
        if chart.track in crown_tracks:
            pass
        else:
            crown_tracks.append(chart.track)
            for artist in chart.track.artists.all():
                if artist in crown_artists:
                    pass
                else:
                    crown_artists.append(artist)

    alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
                 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    for alpha in alphabets:
        alpha_artists = Artist.objects.filter(name__istartswith=alpha).order_by(
            'name').exclude(Q(category__in=[1, 2]) | Q(role=2))
        for artist in alpha_artists:
            if artist in crown_artists:
                artist.crown = True
            else:
                artist.crown = False
        artists[alpha] = alpha_artists
    context['artists'] = artists
    context['inst_artists'] = Artist.objects.filter(
        Q(category__in=[1, 2]) | Q(role=2)).order_by('name')

    return render(request, 'music/artists.html', context)


def artist(request, pk):

    artist = Artist.objects.get(id=pk)
    artist_charts = Chart.objects.filter(artist=artist)
    artist_peak = artist_charts.order_by('rank').first()

    track_set = artist.tracks.all()
    latest_date = Chart.objects.order_by('date').first().date

    tracks = []
    chart_tracks = []
    for track in track_set:
        charts = Chart.objects.filter(track=track)
        cleaned_track = {
            'id': track.id,
            'name': track.name,
            'artist': artist,
            'video': track.video,
        }
        try:
            chart = charts.order_by('rank').first()
            cleaned_track['peak'] = chart.rank
            cleaned_track['date'] = chart.date
            chart_tracks.append(cleaned_track)
        except:
            pass
        finally:
            latest_chart = charts.filter(date=latest_date)
            tracks.append(cleaned_track)

    sorted_tracks = sorted(chart_tracks, key=lambda i: i['peak'])
    context = {
        'artist': artist,
        'tracks': tracks,
        'artist_charts': artist_charts,
        'artist_peak': artist_peak,
        'chart_tracks': sorted_tracks
    }
    return render(request, 'music/artist.html', context)


def get_podcast_playlist():
    podcasts = sp.user_playlist_tracks(
        user, playlist_id=settings.PODCAST_PLAYLIST_ID, fields=None, limit=10, offset=0, market=None)

    return podcasts


def get_track_countries(tracks):
    items = []
    for track in tracks:
        try:
            for artist in track.artists.all():
                if artist.country:
                    items.append(artist.country)
        except:
            pass

    # Counter returns a dict with given value as keys and numbers as values
    collection = collections.Counter(items)

    return collection


def my_autopct(pct):
    return ('%1.1f' % pct) + '%' if pct > 2 else ''


def instruments(request):
    pass


def instrument(request, pk):
    instrument = Instrument.objects.get(id=pk)
    context = {
        'instrument': instrument,
    }

    return render(request, 'music/instrument.html', context)


def chord(request, pk):
    track = Track.objects.get(id=pk)

    context = {
        'track': track,
    }

    return render(request, 'music/chord.html', context)


def chords(request):
    progressions = Progression.objects.all()
    track_list = []

    for progression in progressions:
        if progression.track in track_list:
            pass
        else:
            track_list.append(progression.track)
    context = {
        'tracks': track_list,
        'progressions': progressions
    }
    return render(request, 'music/chords.html', context)


def tracks(reqeust):
    pass


def track(request, pk):
    track = Track.objects.get(id=pk)
    progressions = track.progressions.all().order_by('order')
    context = {
        'track': track,
        'progressions': progressions
    }
    return render(request, 'music/track.html', context)


verrou = RLock()


def getFig():
    dt = datetime.date.today()
    charts = Chart.objects.filter(date=dt).exclude(track=None)
    tracks = []
    for chart in charts:
        tracks.append(chart.track)

    collection = get_track_countries(tracks)

    # Convert dict to list that contains keys(country names)
    countries = list(collection)
    # Extract values(counts) in the dict
    counts = list(collection.values())

    country_list = np.array(countries)
    count_list = np.array(counts)

    c_cycle = ("#3498db", "#51a62d", "#1abc9c", "#9b59b6", "#f1c40f",
               "#7f8c8d", "#34495e", "#446cb3", "#d24d57", "#27ae60",
               "#663399", "#f7ca18", "#bdc3c7", "#2c3e50", "#d35400",
               "#9b59b6", "#ecf0f1", "#ecef57", "#9a9a00", "#8a6b0e")

    fig, (ax1, ax2) = plt.subplots(figsize=(
        10, 7), nrows=1, ncols=2, dpi=80, facecolor='w', edgecolor='k')
    ax1.set(xlabel='Countries', title='Daily Listening Stats.')
    ax1.grid()

    ax1.pie(count_list, labels=country_list,
            colors=c_cycle,
            wedgeprops={'linewidth': 1, 'edgecolor': "white"},
            textprops={'color': "black", 'weight': "normal"},
            startangle=90,
            counterclock=False,
            autopct=lambda p: '{:.1f}%'.format(p) if p >= 5 else '',
            pctdistance=0.7
            )
    ax2.barh(country_list, count_list)
    ax2.grid()

    # ax1.legend(loc="center right", bbox_to_anchor=(0,.5,1.5,0),)

    return fig


def get_svg(request):
    fig = getFig()
    buf = io.BytesIO()
    plt.savefig(buf, format='svg')
    plt.close(fig)
    response = HttpResponse(buf.getvalue(), content_type='image/svg+xml')
    return response


def spotify_json(request):
    path = 'static/common/spotify_api.txt'
    with open(path) as f:
        file = f.read()

    return render(request, 'music/spotify_json.html', {'file': file})


def fetch_plot_svg(fig):
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200)
    plt.close(fig)
    response = HttpResponse(buf.getvalue(), content_type='image/png')
    return response


def plot_track_chart(request, pk):
    with verrou:
        charts = Chart.objects.filter(track=pk).order_by('date')
        track = Track.objects.get(id=pk)
        dt = datetime.datetime.today()
        span = 30
        dt_past = dt - datetime.timedelta(days=span)

        dates = []
        day = dt_past.day
        month = dt_past.month
        year = dt_past.year

        for i in range(span+1):
            try:
                dates.append(datetime.datetime(year, month, day))
            except ValueError:
                day = 1
                month += 1

                try:
                    dates.append(datetime.datetime(year, month, day))
                except ValueError:
                    month = 1
                    year += 1
                dates.append(datetime.datetime(year, month, day))
            finally:
                day += 1

        chart_dates = []
        ranks = []
        dummy_ranks = []

        on_chart_count = 0
        for date in dates:
            try:
                chart = charts.get(date=date)
                chart_date = date
                rank = chart.rank
                on_chart_count += 1
            except:
                chart_date = date
                if on_chart_count == 0:
                    rank = 60  # Change it to None if you don't want to show    the first slope
                    dummy_rank = 60
                else:
                    rank = 60
                    dummy_rank = 60

                # dummy_ranks.append(dummy_rank)
            finally:
                chart_dates.append(chart_date)
                ranks.append(rank)

        average = math.floor(statistics.mean(ranks))
        y2 = [average] * int(span+2)

        cmap = colors.ListedColormap(
            ['red', 'orange', 'yellow', 'green',   'blue'])
        bounds = [1, 10, 20, 30, 40, 50]
        norm = colors.BoundaryNorm(bounds, cmap.N)

        x1 = np.array(dates)
        y1 = np.array(ranks)
        #y2 = np.array(dummy_ranks)

        # Initialize
        fig, ax = plt.subplots(figsize=(
            9, 6), dpi=80, facecolor='w', edgecolor='k')

        ax.set(xlabel='date', ylabel='rank',
               title=track.name)

        # y-axis adjustments
        # order flipped to make it upside-down with a little extra margins
        ax.set_ylim(51, 0)
        yticks = [5 * x for x in np.arange(1, 11)]
        yticks.insert(0, 1)

        ax.set_yticks(yticks)

        # locator settings
        ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

        ax.fill_between(x1, y1, 51, color='#ec7063', alpha=1)

        ax.axhspan(10, 0, facecolor='red', alpha=0.1)
        ax.axhspan(20, 10, facecolor='orange', alpha=0.1)
        ax.axhspan(30, 20, facecolor='yellow', alpha=0.1)
        ax.axhspan(40, 30, facecolor='green', alpha=0.1)
        ax.axhspan(52, 40, facecolor='blue', alpha=0.1)
        ax.grid()

        ax.plot(x1, y1, 'r-', lw=2.5, alpha=0.6, label='ranks')
        ax.plot(x1, y1, 'o', color='orange', markersize=5, markeredgewidth=3,
                markeredgecolor='orange', alpha=0.8)
        ax.plot(x1, y2, 'w--', color="turquoise",
                lw=1.5, alpha=0.8,    label='mean')
        #ax.plot(x1, y2, 'r-', lw=2.5, alpha=0.6, label='theory')

        response = fetch_plot_svg(fig)

        return response


def usages(request):
    usages = Tip.objects.all()

    context = {
        'usages': usages
    }

    return render(request, 'music/usages.html', context)


def usage(request, pk):
    usage = Tip.objects.get(id=pk)
    context = {
        'usage': usage
    }
    return render(request, 'music/usage.html', context)
