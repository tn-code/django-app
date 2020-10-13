import datetime
from django import template
from music.models import Chart, Track

register = template.Library()


@register.simple_tag
def check_track_position(tracks, days):
    dt = datetime.date.today()
    # Note that reset span(days) 0 means next morning.
    last_date = (datetime.datetime.now() -
                 datetime.timedelta(int(days) + 1).strftime('%Y-%m-%d'))

    # Get the latest charts and the last charts
    # MEMO: 'charts' are sets of Chart objects, which is an intermediate table, that respectively have only one track-artist data.
    new_charts = Chart.objects.filter(date=dt).exclude(artist=None)
    last_charts = Chart.objects.filter(date=last_date).exclude(artist=None)

    # Create a list of tracks in the last chart
    last_tracks = []
    for chart in last_charts:
        last_tracks.append(chart['track'])

    # Check position of tracks one by one
    for chart in new_charts:
        track = chart['track']

        # The track found in the last chart
        if track in last_tracks:
            # This case requires to get 2 chart objects, a new chart and a last_chart, to compare their ranks.
            try:
                last_chart = Chart.objects.get(track=track, date=last_date)
            except:
                error = 'No track with a name attribute" ' + \
                    track.name + ' " found in the last chart.'
                return redirect('music:index')

            new_rank = chart['rank']
            last_rank = last_chart['rank']

            # Compare the two ranks to set a position
            if news_rank < last_rank:
                position = 'UP'
            elif news_rank > last_rank:
                position = 'DOWN'
            elif news_rank == last_rank:
                position = 'EQUAL'
            else:
                position = 'UNKNOWN'

        # The track not found in the "LAST" chart
        else:
            # Check if the track ranks in for the first time or comes back again after some out-of-chart time
            try:
                Chart.objects.get(track=track)
                position = 'BACK'
            except:
                position = 'NEW'

        return position
