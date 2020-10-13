from django.contrib import admin
from .models import Term, Sentence, Synonym, Definition, Collocation, Comparison, Occasion, Genre, Derivative, Dialect, Usage, Grammar, Line, Dialogue, Clause
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline

admin.site.register(Synonym)

admin.site.register(Collocation)
admin.site.register(Comparison)
admin.site.register(Occasion)
admin.site.register(Genre)
admin.site.register(Line)

admin.site.register(Grammar)
admin.site.register(Clause)

admin.site.register(Derivative)
admin.site.register(Dialect)


class LineInline(NestedTabularInline):
    model = Line
    extra = 0


class DialogueAdmin(NestedModelAdmin):
    inlines = [LineInline]
    extra = 0


admin.site.register(Dialogue, DialogueAdmin)


class SynonymFromInline(NestedTabularInline):
    model = Synonym
    extra = 0
    fk_name = 'to_term'


class SynonymToInline(NestedTabularInline):
    model = Synonym
    extra = 0
    fk_name = 'from_term'


class UsageInline(NestedTabularInline):
    model = Term.usages.through
    extra = 0
    verbose_name = "Term Usage"
    verbose_name_plural = "Term Usages"


class UsageAdmin(NestedModelAdmin):
    inlines = [UsageInline]
    extra = 0


admin.site.register(Usage, UsageAdmin)


class CollocationInline(NestedTabularInline):
    model = Collocation
    extra = 0


class ClauseInline(NestedTabularInline):
    model = Clause
    extra = 0


class DerivativeDerivativeInline(NestedTabularInline):
    model = Derivative
    extra = 0
    fk_name = 'base'


class DerivativeBaseInline(NestedTabularInline):
    model = Derivative
    extra = 0
    fk_name = 'derivative'


class DefinitionInline(NestedTabularInline):
    model = Definition
    extra = 0
    inlines = [CollocationInline, ClauseInline]


class SentenceInline(NestedStackedInline):
    model = Sentence
    extra = 0
    exclude = ('memo',)


class TermAdmin(NestedModelAdmin):
    search_fields = ('name',)
    inlines = [DefinitionInline, SentenceInline, DerivativeBaseInline,
               DerivativeDerivativeInline, SynonymFromInline, SynonymToInline, UsageInline]
    exclude = ('usages',)


admin.site.register(Term, TermAdmin)


class SentenceAdmin(admin.ModelAdmin):
    search_fields = ['term__name', 'body']


admin.site.register(Sentence, SentenceAdmin)


class DefinitionAdmin(admin.ModelAdmin):
    search_fields = ['term__name']


admin.site.register(Definition, DefinitionAdmin)
