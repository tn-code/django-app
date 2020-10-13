import os
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import date
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower
from django.urls import reverse


def get_image_path(self, filename):
    return os.path.join('images', 'utility', self.__class__.__name__, self.name, filename)


class Schedule(models.Model):
    name = models.CharField(max_length=128)
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    venue = models.CharField(max_length=128, blank=True, null=True)
    company = models.CharField(max_length=128, blank=True, null=True)

    WORK = 'WORK'
    PRIVATE = 'PRIVATE'

    TYPE_CHOICES = [
        (WORK, 'Work'),
        (PRIVATE, 'Private'),
    ]
    type = models.CharField(max_length=32,
                            choices=TYPE_CHOICES, blank=True, null=True, verbose_name="Type")

    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name + ' (' + str(self.date.strftime('%Y/%m/%d - %H:%M')) + ')'

    class Meta:
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'
        ordering = [Lower('name')]

    def get_absolute_url(self):
        return reverse('utility:schedule', kwargs={'pk': self.id})


class Memo(models.Model):
    body = models.TextField()

    def __str__(self):
        return str(self.id) + '. ' + self.body[:20]

    class Meta:
        verbose_name = 'Memo'
        verbose_name_plural = 'Memos'


class Todo(models.Model):
    body = models.CharField(max_length=128)
    comment = models.TextField(blank=True, null=True)
    due = models.DateTimeField(blank=True, null=True)
    label = models.CharField(max_length=128, blank=True, null=True)

    YET = 'YET'
    PROGRESS = 'PROGRESS'
    DONE = 'DONE'
    PENDING = 'PENDING'

    STATUS_CHOICES = [
        (YET, 'YET'),
        (PROGRESS, 'PROGRESS'),
        (DONE, 'DONE'),
        (PENDING, 'PENDING')
    ]

    status = models.CharField(max_length=32,
                              choices=STATUS_CHOICES, null=True)

    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.id) + '. ' + self.body[:20]

    class Meta:
        verbose_name = 'Todo'
        verbose_name_plural = 'Todos'


class Bookmark(models.Model):
    name = models.CharField(max_length=64)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    link = models.URLField(verbose_name="Link")
    type = models.CharField(max_length=64)

    def __str__(self):
        return '{id}. {name}'.format(
            id=self.id,
            name=self.name
        )

    class Meta:
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'


class Item(models.Model):
    body = models.CharField(max_length=128)
    comment = models.TextField(blank=True, null=True)
    step = models.IntegerField(blank=True, null=True)
    due = models.DateTimeField(blank=True, null=True)
    label = models.CharField(max_length=128, blank=True, null=True)
    base = models.ForeignKey(
        Todo, verbose_name="Base", blank=True, null=True, on_delete=models.PROTECT)
    YET = 'YET'
    PROGRESS = 'PROGRESS'
    DONE = 'DONE'
    PENDING = 'PENDING'
    TBC = 'TBC'

    STATUS_CHOICES = [
        (YET, 'YET'),
        (TBC, 'TBC'),
        (PROGRESS, 'PROGRESS'),
        (DONE, 'DONE'),
        (PENDING, 'PENDING')
    ]

    status = models.CharField(max_length=32,
                              choices=STATUS_CHOICES, null=True, blank=True)
    delete_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.body[:20]

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
