import os
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import date
from datetime import datetime

from django.core.exceptions import ValidationError
from embed_video.fields import EmbedVideoField


def get_image_path(self, filename):
    if hasattr(self, 'name'):
        return os.path.join('images', 'music', self.__class__.__name__, self.name, filename)
    else:
        return os.path.join('images', 'music', self.__class__.__name__, self.tip.name, filename)


class Category(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class ArticleTag(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Article Tag'
        verbose_name_plural = 'Article Tags'


class TipCategory(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Tip Category'
        verbose_name_plural = 'Tip Categories'


class Tip(models.Model):
    name = models.CharField(max_length=128)
    categories = models.ManyToManyField(
        TipCategory, related_name="%(class)ss", blank=True)
    tags = models.ManyToManyField(
        ArticleTag, related_name="%(class)ss", blank=True)
    content = models.TextField()
    source_name = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Source")
    instruments = models.ManyToManyField(
        "Instrument", related_name="%(class)ss", blank=True)

    WEBSITE = 'WEBSITE'
    BOOK = 'BOOK'
    YOUTUBE = 'YOUTUBE'

    MEDIA_CHOICES = [
        (WEBSITE, 'Website'),
        (BOOK, 'Book'),
        (YOUTUBE, 'YouTube'),
    ]
    source_media = models.CharField(max_length=32,
                                    choices=MEDIA_CHOICES, blank=True, null=True, verbose_name="Media Type")
    source_link = models.TextField(
        blank=True, null=True, verbose_name="Source Link")

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Tip'
        verbose_name_plural = 'Tips'


class Video(models.Model):
    tip = models.ForeignKey(
        Tip, on_delete=models.CASCADE, related_name='tip_videos')
    video = EmbedVideoField(blank=True)
    caption = models.CharField(max_length=64)


class TipImage(models.Model):
    tip = models.ForeignKey(
        Tip, on_delete=models.CASCADE, related_name='tip_images')
    image = models.ImageField(upload_to=get_image_path)
    source_name = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Source")

    WEBSITE = 'WEBSITE'
    BOOK = 'BOOK'
    YOUTUBE = 'YOUTUBE'

    MEDIA_CHOICES = [
        (WEBSITE, 'Website'),
        (BOOK, 'Book'),
        (YOUTUBE, 'YouTube'),
    ]
    source_media = models.CharField(max_length=32,
                                    choices=MEDIA_CHOICES, blank=True, null=True, verbose_name="Media Type")
    source_link = models.TextField(
        blank=True, null=True, verbose_name="Source Link")
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.id) + '. ' + self.tip.name + ' [' + str(self.created_at) + ']'

    class Meta:
        verbose_name = 'Tip Image'
        verbose_name_plural = 'Tip Images'


class Instrument(models.Model):
    name = models.CharField(max_length=128)
    classification = models.CharField(max_length=128, blank=True, null=True)
    lowest_note = models.CharField(max_length=4, blank=True, null=True)
    highest_note = models.CharField(max_length=4, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Instrument'
        verbose_name_plural = 'Instruments'


class Role(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'


class Artist(models.Model):
    name = models.CharField(max_length=64)
    alias = models.CharField(max_length=64, blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    spotify_id = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, blank=True, null=True)
    is_player = models.BooleanField(default=False)
    instrument = models.ForeignKey(
        Instrument, on_delete=models.PROTECT, blank=True, null=True)
    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Artist'
        verbose_name_plural = 'Artists'

    def clean(self):
        if self.is_player is not True and self.instrument is not None:
            raise ValidationError(
                'You can not assign instrument field to a non-player.')


class Track(models.Model):
    name = models.CharField(max_length=64)
    artists = models.ManyToManyField(
        Artist, related_name="%(class)ss")
    language = models.CharField(max_length=64, null=True, blank=True)
    album = models.CharField(max_length=128, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    key = models.CharField(max_length=64, blank=True, null=True)
    time = models.CharField(max_length=128, blank=True, null=True)
    bpm = models.IntegerField(blank=True, null=True)
    instruments = models.ManyToManyField(
        Instrument, blank=True, related_name="%(class)ss")
    video = EmbedVideoField(blank=True)

    # spotify_id = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return '{id}. {name} － {artist}'.format(
            id=self.id,
            name=self.name,
            artist=self.artists.all()[0].name
        )

    class Meta:
        verbose_name = 'Track'
        verbose_name_plural = 'Tracks'


class Chart(models.Model):
    artist = models.ForeignKey(
        Artist, on_delete=models.PROTECT, related_name='%(class)ss', blank=True, null=True)
    track = models.ForeignKey(
        Track, on_delete=models.PROTECT, related_name='%(class)ss', blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    rank = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)], blank=True, null=True)

    def __str__(self):
        if self.track is not None:
            return 'Track Top 10 ({date}) : [{rank}] {track} － {artist}'.format(
                date=self.date,
                rank=self.rank,
                track=self.track.name,
                artist=self.track.artists.all()[0].name
            )
        else:
            return 'Artist Top 10 ({date}) : [{rank}] {artist}'.format(
                date=self.date,
                rank=self.rank,
                artist=self.artist.name
            )

    class Meta:
        verbose_name = 'Chart'
        verbose_name_plural = 'Charts'

    def clean(self):
        if self.artist is not None and self.track is not None:
            raise ValidationError(
                'You must select only one of those fields: "Artist" or "Track".')
        elif self.artist is None and self.track is None:
            raise ValidationError(
                'You must select one of those fields: "Artist"" or "Track".')


class Progression(models.Model):
    track = models.ForeignKey(
        Track, on_delete=models.PROTECT, related_name='%(class)ss')
    chord = models.CharField(max_length=32)
    numeral = models.CharField(max_length=32, blank=True, null=True)
    order = models.IntegerField()
    lyrics = models.CharField(max_length=128, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return '{id}. {track} [{order}] {chord}'.format(
            id=self.id,
            track=self.track.name,
            order=self.order,
            chord=self.chord
        )

    class Meta:
        verbose_name = 'Progression'
        verbose_name_plural = 'Progressions'
        constraints = [
            models.UniqueConstraint(
                fields=['track', 'order'], name='unique_track_order')
        ]
