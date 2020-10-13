from django.contrib import admin
from .models import Term, Sentence, Definition, Usage
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline



class UsageInline(NestedTabularInline):
    model = Term.usages.through
    extra = 0
    verbose_name = "Term Usage"
    verbose_name_plural = "Term Usages"


class UsageAdmin(NestedModelAdmin):
    inlines = [UsageInline]
    extra = 0


admin.site.register(Usage, UsageAdmin)


class DefinitionInline(NestedTabularInline):
    model = Definition
    extra = 0


class SentenceInline(NestedStackedInline):
    model = Sentence
    extra = 0


class TermAdmin(NestedModelAdmin):
    search_fields = ('name',)
    inlines = [DefinitionInline, SentenceInline, UsageInline]
    exclude = ('usages',)


admin.site.register(Term, TermAdmin)


class SentenceAdmin(admin.ModelAdmin):
    search_fields = ['term__name', 'body']


admin.site.register(Sentence, SentenceAdmin)


class DefinitionAdmin(admin.ModelAdmin):
    search_fields = ['term__name']


admin.site.register(Definition, DefinitionAdmin)
