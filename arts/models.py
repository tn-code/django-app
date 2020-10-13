import os
from datetime import date

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.safestring import mark_safe


def get_image_path(self, filename):
    return os.path.join('images', 'arts', self.__class__.__name__, self.name, filename)


def get_work_image_path(self, filename):
    return os.path.join('images', 'arts', self.title, filename)


def get_design_image_path(self, filename):
    return os.path.join('images', 'arts', self.__class__.__name__, self.category, filename)


class Museum(models.Model):
    name = models.CharField(max_length=128)
    name_en = models.CharField(max_length=128)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    country = models.CharField(max_length=256)
    city = models.CharField(max_length=256)
    established_at = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(2020)], blank=True, null=True)
    website = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    permanent = models.BooleanField(default=False)
    special = models.BooleanField(default=False)

    OPENED = 'OPENED'
    TEMP_CLOSED = 'TEMP_CLOSED'
    PERM_CLOSED = 'PERM_CLOSED'

    STATUS_CHOICES = (
        (OPENED, 'Opened'),
        (TEMP_CLOSED, 'Temporarily Closed'),
        (PERM_CLOSED, 'Permanently Closed'),
    )
    status = models.CharField(max_length=32,
                              choices=STATUS_CHOICES, null=True)
    status_detail = models.TextField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Museum'
        verbose_name_plural = 'Museums'


class Exhibition(models.Model):
    name = models.CharField(max_length=128)
    name_en = models.CharField(max_length=256, blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)
    venue = models.CharField(max_length=128, blank=True, null=True)
    open_at = models.DateField(default=date.today, blank=True, null=True)
    close_at = models.DateField(default=date.today, blank=True, null=True)
    visited_at = models.DateField(default=date.today, blank=True, null=True)
    museum = models.ForeignKey(
        Museum, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Exhibition'
        verbose_name_plural = 'Exhibitions'


class Genre(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'


class Artist(models.Model):
    name_jp = models.CharField(max_length=64)
    name = models.CharField(max_length=64, blank=True, null=True)
    birth_date = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(2020)], blank=True, null=True)
    death_date = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(2020)], blank=True, null=True)
    country = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)
    genre = models.ManyToManyField(
        Genre, related_name="%(class)ss_related")
    image = models.ImageField(
        upload_to=get_image_path, blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name_jp

    class Meta:
        verbose_name = 'Artist'
        verbose_name_plural = 'Artists'


class Work(models.Model):
    title_jp = models.CharField(max_length=512)
    title = models.CharField(max_length=512, blank=True, null=True)
    artist = models.ForeignKey(
        Artist, blank=True, null=True, on_delete=models.PROTECT)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to=get_work_image_path, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    creation_date = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(2020)], blank=True, null=True)
    museum = models.ForeignKey(
        Museum, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.title_jp

    class Meta:
        verbose_name = 'Work'
        verbose_name_plural = 'Works'


class Tag(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class Design(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    designer = models.CharField(max_length=128, blank=True, null=True)
    image = models.ImageField(
        upload_to=get_design_image_path, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name="%(class)ss", blank=True)

    BANNER = 'BANNER'
    LOGO = 'LOGO'
    VECTOR = 'VECTOR'
    TYPOGRAPHY = 'TYPOGRAPHY'
    ARTWORK = 'ARTWORK'
    MISC = 'MISC'

    CATEGORY_CHOICES = [
        (MISC, 'Misc'),
        (BANNER, 'Banner'),
        (LOGO, 'Logo'),
        (TYPOGRAPHY, 'Typography'),
        (VECTOR, 'Vector'),
        (ARTWORK, 'Artwork')
    ]

    category = models.CharField(max_length=32,
                                choices=CATEGORY_CHOICES, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.category

    def admin_image(self):
        if self.image:
            return mark_safe('<img src="{}" style="width:100px; height:auto;">'.format(self.image.url))
        else:
            return 'no image'

    admin_image.allow_tags = True

    class Meta:
        verbose_name = 'Design'
        verbose_name_plural = 'Designs'
