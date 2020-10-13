from django.contrib import admin
from .models import Schedule, Todo, Bookmark, Item
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline

admin.site.register(Schedule)

admin.site.register(Item)
admin.site.register(Bookmark)


class ItemInline(NestedTabularInline):
    model = Item
    extra = 0


class TodoAdmin(NestedModelAdmin):
    search_fields = ('name',)
    inlines = [ItemInline]


admin.site.register(Todo, TodoAdmin)
