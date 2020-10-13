from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from calendar import HTMLCalendar
from django.utils.html import conditional_escape as esc
from itertools import groupby
from datetime import date
import datetime
from django import template
from django.contrib.auth.models import User
from utility.models import Schedule, Todo, Bookmark, Item
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.db.models import Q


def todos(request):
    todos = Todo.objects.all()
    done = Item.objects.filter(status='DONE')
    context = {
        'todos': todos,
        'done': done
    }
    return render(request, 'utility/todos.html', context)


class ScheduleCalendar(HTMLCalendar):

    def __init__(self, schedules):
        super(ScheduleCalendar, self).__init__()
        self.schedules = self.group_by_day(schedules)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
            if day in self.schedules:
                cssclass += ' filled'
                body = ['<ul>']
                for schedule in self.schedules[day]:
                    body.append('<li>')
                    body.append('<a href="%s">' % schedule.get_absolute_url())
                    body.append(esc(schedule.name))
                    body.append('</a></li>')
                body.append('</ul>')
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
        return '<td class="%s">%s</td>' % (cssclass, body)


def calendar():
    today = datetime.date.today()
    year = today.year
    month = today.month
    my_schedules = Schedule.objects.order_by('date').filter(
        date__year=year, date__month=month
    )
    cal = ScheduleCalendar(my_schedules).formatmonth(year, month)

    return cal


def index(request):
    pass


def schedules(request):
    calendar = calendar()
    context = {
        'calendar': calendar
    }
    return render(request, 'utility/schedules.html', context)


def schedule(request, pk):
    context = {}
    return render(request, 'utility/schedule.html', context)
