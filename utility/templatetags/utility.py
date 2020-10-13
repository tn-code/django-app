from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from calendar import HTMLCalendar
from django.utils.html import conditional_escape as esc
from itertools import groupby
from datetime import date
import datetime
from django import template
from django.contrib.auth.models import User
from utility.models import Schedule
from django.utils import formats
import holidays
from utility.models import Todo
register = template.Library()


@register.simple_tag
def get_current_time(format_string):
    return datetime.datetime.now().strftime(format_string)


@register.simple_tag
def get_day_of_week():
    return datetime.date.today().strftime('%A')[:3]


@register.simple_tag
def get_nav_items():
    nav_items = ['1', '2', '3']
    context = {'nav_items': nav_items}
    return context


@register.simple_tag
def append_bootstrap_alert_class(tags):
    return 'alert alert-danger' if tags == 'error' else 'alert alert-success' if tags == 'success' else 'alert alert-warning' if tags == 'warning' else 'alert alert-info' if tags == 'info' else tags


@register.simple_tag
def get_superuser(request):
    return User.objects.get(id=request.POST.get('id')).username


class ScheduleCalendar(HTMLCalendar):

    def __init__(self, schedules):
        super(ScheduleCalendar, self).__init__()
        self.schedules = self.group_by_day(schedules)

        self.setfirstweekday(6)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]

            jp_holidays = []
            for holiday in holidays.Japan(years=2019).items():
                jp_holidays.append(str(holiday[0]))
            my_date = date(self.year, self.month, day)
            weeknum = int(my_date.strftime('%U')) % 4
            thisweeknum = int(date.today().strftime('%U')) % 4
            cssclass += ' week' + str(weeknum + 1)
            if weeknum == thisweeknum:
                cssclass += ' thisweek'
            if date.today() == my_date:
                cssclass += ' today'
            if str(my_date) in jp_holidays:
                cssclass += 'public-holiday'
            if day in self.schedules:
                cssclass += ' filled'
                body = ['<ul class="schedule-list">']
                for schedule in self.schedules[day]:
                    if schedule.type == 'PRIVATE':
                        body.append('<li class="schedule-item private">')
                    else:
                        body.append('<li class="schedule-item">')
                    body.append('<a href="%s">' % schedule.get_absolute_url())
                    item = schedule.name
                    if schedule.date:
                        item = item + '(' + \
                            str(schedule.date.strftime('%H:%M'))
                    if schedule.venue:
                        item = item + schedule.venue + ')'
                    else:
                        item = item + ')'
                    body.append(
                        esc(item))
                    body.append('</a></li>')
                body.append('</ul>')
                return self.day_cell(cssclass, '%d %s' % (day, ''.join(body)))
            else:
                body = ['<span class="add-schedule">']
                body.append(
                    '<a href="http://127.0.0.1:8000/admin/utility/schedule/add/"></a>')
                return self.day_cell(cssclass, '%d %s' % (day, ''.join(body)))

            return self.day_cell(cssclass, day)
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(ScheduleCalendar, self).formatmonth(year, month)

    def group_by_day(self, schedules):
        def field(schedule): return schedule.date.day
        return dict(
            [(day, list(items)) for day, items in groupby(schedules, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s day-cell">%s</td>' % (cssclass, body)


@register.simple_tag
def calendar():
    today = datetime.date.today()
    year = today.year
    month = today.month
    my_schedules = Schedule.objects.order_by('date').filter(
        date__year=year, date__month=month
    )
    cal = ScheduleCalendar(my_schedules).formatmonth(year, month)
    return mark_safe(cal)


@register.simple_tag
def todos():
    todos = Todo.objects.all()
    return todos
