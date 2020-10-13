import os
from datetime import date
from datetime import datetime
from django.db import models


def get_image_path(self, filename):
    return os.path.join('images', 'lib', self.__class__.__name__, self.name, filename)


def get_quote_image_path(self, filename):
    return os.path.join('images', 'lib', str(self.id) + '. ' + self.body[:10], filename)


class Category(models.Model):
    name = models.CharField(max_length=128)
    name_en = models.CharField(max_length=128, null=True, blank=True)
    description = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Tag(models.Model):
    name = models.CharField(max_length=128)
    name_en = models.CharField(max_length=128, null=True, blank=True)
    description = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class Terminology(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=512, blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Terminology'
        verbose_name_plural = 'Terminologies'


class Book(models.Model):
    name = models.CharField(max_length=128)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    publisher = models.CharField(max_length=64, blank=True, null=True)
    published_at = models.DateField(default=date.today)
    categories = models.ManyToManyField(
        Category,  blank=True)
    tags = models.ManyToManyField(
        Tag, blank=True)
    author = models.CharField(max_length=64, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    read_at = models.DateField(blank=True, null=True)
    purchased_at = models.DateField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    rate = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'


class Quote(models.Model):
    body = models.TextField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to=get_quote_image_path, blank=True, null=True)
    terminologies = models.ManyToManyField(
        Terminology, related_name="%(class)ss_related", blank=True)
    quotes = models.ManyToManyField('self', verbose_name="関連引用", blank=True,
                                    symmetrical=False,
                                    related_name='%(class)ss_related')

    def __str__(self):
        return str(self.id) + '. ' + self.body[:20] + '  －  <' + self.book.name[:20] + '>'

    class Meta:
        verbose_name = 'Quote'
        verbose_name_plural = 'Quotes'


class Memo(models.Model):
    body = models.TextField()
    source = models.CharField(max_length=512, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    CUISINE = 'CUISINE'
    ENGLISH = 'ENGLISH'
    LIBRARY = 'LIBRARY'

    CATEGORY_CHOICES = [
        (CUISINE, 'Cuisine'),
        (ENGLISH, 'English'),
        (LIBRARY, 'Library')
    ]

    category = models.CharField(max_length=32,
                                choices=CATEGORY_CHOICES, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.body[:20] + '  －  <' + self.source[:20] + '>'

    class Meta:
        verbose_name = 'Memo'
        verbose_name_plural = 'Memos'


class Theme(models.Model):
    name = models.CharField(max_length=128)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, blank=True, null=True)
    quotes = models.ManyToManyField(Quote, blank=True)
    comment = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    description = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Theme'
        verbose_name_plural = 'Themes'
