from django.contrib import admin
from .models import Medicine, Intake, Ingredient, Effect, Term, Document, Precaution, SideEffect, Property, Client, MedicineImage, TermImage, SymptomImage, Symptom, Law, Article, PropertyImage, RelatedIngredient, Description, Category, IngredientImage, ReferenceImage, Disease, DiseaseImage, CategoryImage, Summary, RelatedMedicine
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline
from django_summernote.admin import SummernoteModelAdmin
from embed_video.admin import AdminVideoMixin

admin.site.register(Intake)

admin.site.register(Client)
admin.site.register(Effect)
admin.site.register(Document)
admin.site.register(Precaution)
admin.site.register(SideEffect)
admin.site.register(Law)

admin.site.register(ReferenceImage)


class SummaryInline(NestedTabularInline):

    model = Summary
    extra = 0


class SummaryAdmin(NestedModelAdmin):
    model = Summary
    extra = 0


admin.site.register(Summary, SummaryAdmin)


class CategoryImageInline(NestedTabularInline):
    model = CategoryImage
    extra = 0


class CategoryAdmin(NestedModelAdmin):
    inlines = [CategoryImageInline]
    extra = 0


admin.site.register(Category, CategoryAdmin)


class DiseaseImageInline(NestedTabularInline):
    model = DiseaseImage
    extra = 0


class TermInline(NestedTabularInline):
    model = Term.diseases.through
    extra = 0


class DiseaseIngredientInline(NestedTabularInline):
    model = Ingredient.diseases.through
    extra = 0


class DiseaseAdmin(NestedModelAdmin):

    search_fields = ('name',)
    list_display = ('name',)
    inlines = [DiseaseImageInline, TermInline, DiseaseIngredientInline]
    extra = 0
    exclude = ('terms', 'ingredients')


admin.site.register(Disease, DiseaseAdmin)


class PropertyImageInline(NestedTabularInline):
    model = PropertyImage
    extra = 0


class PropertyAdmin(NestedModelAdmin):

    search_fields = ('name',)
    list_display = ('name',)
    inlines = [PropertyImageInline]
    extra = 0


admin.site.register(Property, PropertyAdmin)


class ArticleAdmin(SummernoteModelAdmin):
    summernote_fields = 'body'


admin.site.register(Article, ArticleAdmin)


class MedicineImageInline(NestedTabularInline):
    model = MedicineImage
    extra = 0


class IngredientImageInline(NestedTabularInline):
    model = IngredientImage
    extra = 0


class TermImageInline(NestedTabularInline):
    model = TermImage
    extra = 0


class TermAdmin(AdminVideoMixin, NestedModelAdmin):

    search_fields = ('name',)
    list_display = ('name',)
    inlines = [TermImageInline]
    extra = 0


admin.site.register(Term, TermAdmin)


class SymptomImageInline(NestedTabularInline):
    model = SymptomImage
    extra = 0


class SymptomAdmin(NestedModelAdmin):

    search_fields = ('name',)
    list_display = ('name',)
    inlines = [SymptomImageInline, ]
    extra = 0


admin.site.register(Symptom, SymptomAdmin)


class ClientInline(NestedTabularInline):
    model = Client
    extra = 0


class IngredientEffectInline(NestedTabularInline):
    model = Ingredient.effects.through
    extra = 0
    verbose_name = "効能 ー Effect"
    verbose_name_plural = "効能 ー Effects"


class PrecautionInline(NestedTabularInline):
    model = Ingredient.precautions.through
    extra = 0
    verbose_name = "注意事項 ー Precaution"
    verbose_name_plural = "注意事項 ー Precautions"


class SymptomInline(NestedTabularInline):
    model = Ingredient.symptoms.through
    extra = 0
    verbose_name = "症状 ー Symptoms"
    verbose_name_plural = "症状 ー Symptoms"


class ReferenceInline(NestedTabularInline):
    model = Ingredient.references.through
    extra = 0
    verbose_name = "関連用語 ー Reference"
    verbose_name_plural = "関連用語 ー References"


class SideEffectInline(NestedTabularInline):
    model = Ingredient.side_effects.through
    extra = 0
    verbose_name = "副作用ー Side Effect"
    verbose_name_plural = "副作用 ー Side Effects"


class PropertyInline(NestedTabularInline):
    model = Ingredient.properties.through
    extra = 0
    verbose_name = "性質 ー Property"
    verbose_name_plural = "性質 ー Properties"


class RelatedIngredientInline(NestedTabularInline):
    model = RelatedIngredient
    extra = 0
    fk_name = 'base'
    verbose_name = "関連成分 ー Related Ingredient"
    verbose_name_plural = "関連成分 ー Related Ingredients"


class IngredientAdmin(AdminVideoMixin, NestedModelAdmin):

    search_fields = ('name',)
    list_display = ('name', 'alias', 'name_en', 'formula', 'admin_image', 'id')
    inlines = [PropertyInline, IngredientEffectInline, SymptomInline, RelatedIngredientInline,  ReferenceInline, PrecautionInline,
               SideEffectInline, IngredientImageInline, SummaryInline]
    exclude = ('ingredients', 'effects', 'properties',
               'side_effects', 'precautions', 'references', 'symptoms', 'iupac', 'pronunciation', 'compositions')
    extra = 0


admin.site.register(Ingredient, IngredientAdmin)


class IngredientInline(NestedTabularInline):
    model = Medicine.ingredients.through
    extra = 0
    verbose_name = "Medicine Ingredient"
    verbose_name_plural = "Medicine Ingredients"


class EffectInline(NestedTabularInline):
    model = Medicine.effects.through
    extra = 0
    verbose_name = "Medicine Effect"
    verbose_name_plural = "Medicine Effects"


class RelatedMedicineInline(NestedTabularInline):
    model = RelatedMedicine
    extra = 0
    fk_name = 'base'
    verbose_name = "関連医薬品 ー Related Medicine"
    verbose_name_plural = "関連医薬品 ー Related Medicines"


class MedicineAdmin(AdminVideoMixin, NestedModelAdmin):

    search_fields = ('name',)
    list_display = ('name', 'publisher', 'link', 'id')
    inlines = [IngredientInline, EffectInline,
               MedicineImageInline, RelatedMedicineInline]
    exclude = ('ingredients', 'effects', 'relationships')
    extra = 0


admin.site.register(Medicine, MedicineAdmin)
