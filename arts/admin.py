from django.contrib import admin
from .models import Exhibition, Work, Genre, Artist, Design, Museum, Tag
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline

admin.site.register(Exhibition)
admin.site.register(Work)
admin.site.register(Genre)
admin.site.register(Artist)
admin.site.register(Tag)
admin.site.register(Museum)


class TagInline(NestedTabularInline):
    model = Design.tags.through
    extra = 0


class DesignAdmin(NestedModelAdmin):

    search_fields = ('name',)
    list_display = ('admin_image', 'category', 'id', )
    inlines = [TagInline]
    extra = 0


admin.site.register(Design, DesignAdmin)
