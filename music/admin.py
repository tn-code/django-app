from embed_video.admin import AdminVideoMixin
from django.contrib import admin
from .models import Artist, Track, Chart, Progression, Category, Instrument, Role, Tip, TipImage, TipCategory, ArticleTag
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline

admin.site.register(Chart)
admin.site.register(Progression)
admin.site.register(Category)
admin.site.register(Role)
admin.site.register(Instrument)
admin.site.register(TipImage)
admin.site.register(TipCategory)
admin.site.register(ArticleTag)


class TipImageInline(NestedTabularInline):
    model = TipImage
    extra = 0


class TipCategoryInline(NestedTabularInline):
    model = Tip.categories.through
    extra = 0
    verbose_name = "Tip Category"
    verbose_name_plural = "Tip Categories"


class TipInstrumentInline(NestedTabularInline):
    model = Tip.instruments.through
    extra = 0


class TipTagInline(NestedTabularInline):
    model = Tip.tags.through
    extra = 0


class TipAdmin(NestedModelAdmin):
    search_fields = ('title',)
    inlines = [TipImageInline, TipCategoryInline,
               TipTagInline, TipInstrumentInline]
    exclude = ("categories", "instruments", "tags")


admin.site.register(Tip, TipAdmin)


class ProgressionInline(NestedTabularInline):
    model = Progression
    extra = 0


class InstrumentInline(NestedTabularInline):
    model = Track.instruments.through
    extra = 0


class TrackInline(NestedTabularInline):
    model = Artist.tracks.through
    extra = 0
    verbose_name = "Artist Track"
    verbose_name_plural = "Artist Tracks"


class TrackAdmin(AdminVideoMixin, NestedModelAdmin):

    search_fields = ('name',)
    list_display = ('name', 'video')
    inlines = [TrackInline, InstrumentInline, ProgressionInline]
    extra = 0

    exclude = ('artists', 'instruments')


admin.site.register(Track, TrackAdmin)


class ArtistAdmin(NestedModelAdmin):

    search_fields = ('name',)
    inlines = [TrackInline]


admin.site.register(Artist, ArtistAdmin)
