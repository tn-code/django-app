import datetime
import time
import urllib.request
import urllib.error
import math

from django.shortcuts import render
from django.conf import settings
from django.core.cache import cache
from django.contrib import messages

from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY)


# dict to retrieve and populate the news api contents
contents = {}
sources = {
    'us': {'type': 'headlines', 'domain': None, 'slice': 10},
    'gb': {'type': 'headlines', 'domain': None, 'slice': 10},
    'ca': {'type': 'headlines', 'domain': None, 'slice': 3},
    'au': {'type': 'headlines', 'domain': None, 'slice': 3},
    'my': {'type': 'headlines', 'domain': None, 'slice': 3},
    'ph': {'type': 'headlines', 'domain': None, 'slice': 3},
    'ie': {'type': 'headlines', 'domain': None, 'slice': 3},
    'za': {'type': 'headlines', 'domain': None, 'slice': 3},
    'nz': {'type': 'sources', 'domain': 'stuff.co.nz', 'slice': 3},
    'jp': {'type': 'sources', 'domain': 'nhk.or.jp', 'slice': 10},
}


def sec_to_datetime(sec):
    days = int(sec) / (24 * 60 * 60)
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


def format_reset_ttl(var):
    hours = math.floor(var / (60 * 60))
    sec = hours * 60 * 60
    minutes = math.floor((var - sec) / 60)
    return 'Next Update: {} hrs {} minutes'.format(hours, minutes)


def check_online():
    # check internet connection by trying accessing to google search page.
    try:
        urllib.request.urlopen('http://216.58.192.142', timeout=1)
        return True
    except urllib.error.URLError as err:
        return False


def fetch_news_data():
    for k, v in sources.items():
        if cache.ttl('reset') == 0:
            if v['type'] == 'headlines':
                contents[k] = newsapi.get_top_headlines(
                    country=k)
            elif v['type'] == 'sources':
                contents[k] = newsapi.get_everything(
                    domains=v['domain'])
            else:
                return render(request, 'news/index.html', {
                    'error': "Something went wrong while fetching data."
                })

            cache.set("news_" + k,
                      contents[k], timeout=None)
        else:
            contents[k] = cache.get('news_' + k)


def calc_cache_expiration():
    if cache.ttl('reset') == 0:
        dt = datetime.datetime.now()
        reset_time = {'morning': 6, 'night': 18}
        morning_sec = reset_time['morning'] * 60 * 60
        night_sec = reset_time['night'] * 60 * 60
        current_hrs_sec = int(dt.hour) * 60 * 60
        current_min_sec = int(dt.hour) * 60
        # Work out remaining time to set reset caches in order to flush db at certain times.
        # If current time in range of morning - night
        if int(dt.hour) in range(reset_time['morning'], reset_time['night']):
            # Remaining hours calculated in seconds
            reset_ttl = night_sec - current_hrs_sec - current_min_sec
        # When current time in range of 18:00 - 6:00
        else:
            elapsed_sec = current_hrs_sec + current_min_sec - morning_sec
            # Determine the remaining time to get to next reset time.
            # 0:00 - morning time comes up with negative hence get abs value
            if elapsed_sec < 0:
                reset_ttl = abs(elapsed_sec)
            # For night time - 23:59 subtract the elapsed time from 24 hours to get remaining time
            else:
                reset_ttl = (60 * 60 * 24) - elapsed_sec
        # Set new cache with reset_ttl vaiable
        cache.set("reset", True, timeout=reset_ttl)
    else:
        reset_ttl = cache.get('reset')

    return reset_ttl


def index(request):

    # Return dict keys as a list with all countries
    ls = list(sources)
    # Check if all the caches exist
    if all([cache.get('news_' + i) for i in ls]) and cache.ttl('reset'):
        for i in ls:
            contents[i] = cache.get('news_' + str(i))
        is_cached = True
        is_online = check_online()
        reset_ttl = cache.ttl('reset')

    # If caches doesn't exist (including the first access after certain reset times)
    else:
        # Check the internet connection in order to fetch data
        if check_online() == False:
            is_online = False
            messages.danger(
                request, 'Unable to display contents due to no existance of caches and internet connection')
            return render(request, 'news/index.html')
        # Fetching data online
        else:
            is_cached = False
            is_online = True

            fetch_news_data()

            # MEMO: Required only when you run this app on the local server
            rest_ttl = calc_cache_expiration()
            messages.success(
                request, 'Contents have been updated successfully!')

    context = {}

    for k, v in sources.items():
        var = 'articles_' + k
        context[var] = contents[k]['articles'][:v['slice']]

    if cache.ttl('reset'):
        reset_ttl = cache.ttl('reset')

    context.update({
        'is_online': is_online,
        'is_cached': is_cached,
        'reset_ttl': sec_to_datetime(reset_ttl),
        'us_ttl': cache.ttl('news_us'),
        'nz_ttl': cache.ttl('news_nz'),
        'gb_ttl': cache.ttl('news_gb'),
        'jp_ttl': cache.ttl('news_jp'),
        'au_ttl': cache.ttl('news_au'),
        'my_ttl': cache.ttl('news_my'),
        'ph_ttl': cache.ttl('news_ph'),
    })
    return render(request, 'news/index.html', context)
