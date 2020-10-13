import os
from datetime import date
from datetime import datetime
from django.db import models
from embed_video.fields import EmbedVideoField
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError

attr_list = [
    'medicine',
    'ingredient',
    'term',
    'disease',
    'property',
    'symptom',
]


def get_image_path(self, filename):
    if self.__class__.__name__ == 'ReferenceImage':
        # set a correct path for an image
        def set_variable_path():
            i = 0
            while i < len(attr_list):
                target = getattr(self, attr_list[i])
                if target:
                    return os.path.join('images', 'pharmacy', 'references', attr_list[i], getattr(target, 'name'), filename)
                else:
                    i += 1

        return set_variable_path()

    else:
        for attr in attr_list:
            # pick up 'name' attribute of a related object
            if hasattr(self, attr):
                return os.path.join('images', 'pharmacy', self.__class__.__name__, getattr(getattr(self, attr), 'name'), filename)
            # when object itself has an 'name' attribute
            elif hasattr(self, 'name'):
                return os.path.join('images', 'pharmacy', self.__class__.__name__, self.name, filename)
            else:
                return 'Failed to set an image path.'


class Effect(models.Model):
    name = models.CharField(max_length=128)
    name_en = models.CharField(max_length=128, null=True, blank=True)
    memo = models.TextField(null=True, blank=True)

    precautions = models.ManyToManyField(
        'Precaution', related_name="%(class)ss", blank=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Effect'
        verbose_name_plural = 'Effects'


class Client(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'


class Precaution(models.Model):
    name = models.CharField(max_length=128)
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, null=True, blank=True)

    PRECAUTION = 'PRECAUTION'
    CONSULTATION = 'CONSULTATION'
    PROHIBITION = 'PROHIBITION'

    TYPE_CHOICES = [
        (PRECAUTION, 'Precaution'),
        (CONSULTATION, 'Consultation'),
        (PROHIBITION, 'Prohibition'),
    ]

    type = models.CharField(max_length=64,
                            choices=TYPE_CHOICES, blank=True)
    symptoms = models.ManyToManyField(
        'SideEffect', related_name="%(class)ss", blank=True)
    memo = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.client:

            return str(self.id) + '. ' + str(self.type) + ':' + str(self.client.name) + ' - ' + str(self.name)
        else:
            return str(self.id) + '. ' + str(self.type) + ':' + ' - ' + str(self.name)

    class Meta:
        verbose_name = 'Precaution'
        verbose_name_plural = 'Precautions'


class SideEffect(models.Model):
    name = models.CharField(max_length=128)
    name_en = models.CharField(max_length=128, null=True, blank=True)
    memo = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Side Effect'
        verbose_name_plural = 'Side Effects'


class Disease(models.Model):
    name = models.CharField(max_length=128)
    name_en = models.CharField(max_length=128, null=True, blank=True)
    memo = models.TextField(blank=True, null=True)
    terms = models.ManyToManyField(
        'Term', related_name="%(class)ss", blank=True)
    ingredients = models.ManyToManyField(
        'Ingredient', related_name="%(class)ss", blank=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Disease'
        verbose_name_plural = 'Diseases'


class DiseaseImage(models.Model):
    disease = models.ForeignKey(
        Disease, on_delete=models.CASCADE, related_name='property_images')
    image = models.ImageField(upload_to=get_image_path)
    created_at = models.DateField(auto_now_add=True)
    caption = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.disease.name + ' [' + str(self.created_at) + ']'

    class Meta:
        verbose_name = 'Disease Image'
        verbose_name_plural = 'Disease Images'


class Category(models.Model):
    name = models.CharField(max_length=128)
    name_en = models.CharField(max_length=128, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    symptoms = models.ManyToManyField(
        "Symptom", related_name="%(class)ss", blank=True)
    precautions = models.ManyToManyField(
        Precaution, related_name="%(class)ss", blank=True)
    properties = models.ManyToManyField(
        "Property", related_name="%(class)ss", blank=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class CategoryImage(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='category_images')
    image = models.ImageField(upload_to=get_image_path)
    created_at = models.DateField(auto_now_add=True)
    caption = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.category.name + ' [' + str(self.created_at) + ']'

    class Meta:
        verbose_name = 'Category Image'
        verbose_name_plural = 'Category Images'


class Property(models.Model):
    name = models.CharField(max_length=128)
    name_en = models.CharField(max_length=128, null=True, blank=True)
    memo = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    side_effects = models.ManyToManyField(
        'SideEffect', related_name="%(class)ss", blank=True)
    precautions = models.ManyToManyField(
        Precaution, related_name="%(class)ss", blank=True)
    video = EmbedVideoField(blank=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'


class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='property_images')
    image = models.ImageField(upload_to=get_image_path)
    created_at = models.DateField(auto_now_add=True)
    caption = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.property.name + ' [' + str(self.created_at) + ']'

    class Meta:
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Images'


class Symptom(models.Model):
    name = models.CharField(max_length=128)
    name_en = models.CharField(max_length=128, null=True, blank=True)
    alias = models.CharField(max_length=128, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    terms = models.ManyToManyField(
        'Term', related_name="%(class)ss", blank=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name + ' - ' + self.name_en

    class Meta:
        verbose_name = 'Symptom'
        verbose_name_plural = 'Symptom'


class SymptomImage(models.Model):
    symptom = models.ForeignKey(
        Symptom, on_delete=models.CASCADE, related_name='symptom_images')
    image = models.ImageField(upload_to=get_image_path)
    created_at = models.DateField(auto_now_add=True)
    caption = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.symptom.name + ' [' + str(self.created_at) + ']'

    class Meta:
        verbose_name = 'Symptom Image'
        verbose_name_plural = 'Symptom Images'


class Description(models.Model):
    body = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.related_ingredient.name:
            return "{0}. {1}".format(str(self.id), self.related_ingredient.name)
        else:
            return "{0}. {1}".format(str(self.id), self.body[:60])

    class Meta:
        verbose_name = 'Description'
        verbose_name_plural = 'Descriptions'


class RelatedIngredient(models.Model):
    base = models.ForeignKey(
        'Ingredient', on_delete=models.CASCADE, related_name='base')
    related = models.ForeignKey(
        'Ingredient', on_delete=models.CASCADE, related_name='related')

    def __str__(self):
        return "{id}. {related} - {base}".format(
            id=str(self.id),
            related=self.related.name,
            base=self.base.name
        )

    class Meta:
        verbose_name = 'Related Ingredient'
        verbose_name_plural = 'Related Ingredients'

        # NOTE: making A-B and B-A combination treated as the same to prevent duplication.
        # Doesn't matter which one goes to which in terms of mutuality
        constraints = [
            models.UniqueConstraint(
                fields=['base', 'related'], name='unique_related'),
        ]

    # override methods for mutual relationships
    # NOTE: when A-B relationship is built/deleted, so is B-A.
    def save(self, *args, **kwargs):
        self.related.relationships.add(self.base)
        super(RelatedIngredient, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.related.relationships.remove(self.base)
        super(RelatedIngredient, self).delete(*args, **kwargs)


class Summary(models.Model):
    body = models.CharField(max_length=256)
    ingredient = models.OneToOneField(
        'Ingredient', on_delete=models.CASCADE, related_name='%(class)s')

    def __str__(self):
        return "{0}. {1}".format(str(self.id), self.ingredient.name)

    class Meta:
        verbose_name = 'Summary'
        verbose_name_plural = 'Summaries'


class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    name_en = models.CharField(max_length=128, null=True, blank=True)
    alias = models.CharField(max_length=128, null=True, blank=True)
    iupac = models.CharField(max_length=128, blank=True, null=True)
    formula = models.CharField(max_length=128, null=True, blank=True)
    compositions = models.ManyToManyField(
        'self', blank=True)
    relationships = models.ManyToManyField(
        'self', verbose_name="Related Ingredients", blank=True, symmetrical=False, related_name='related_%(class)ss', through='RelatedIngredient')
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)

    effects = models.ManyToManyField(
        Effect, related_name="%(class)ss", blank=True)
    memo = models.TextField(blank=True, null=True)
    pronunciation = models.CharField(max_length=128, blank=True, null=True)
    precautions = models.ManyToManyField(
        Precaution, related_name="%(class)ss", blank=True)

    side_effects = models.ManyToManyField(
        SideEffect, related_name="%(class)ss", blank=True)

    properties = models.ManyToManyField(
        Property, related_name="%(class)ss", blank=True)
    symptoms = models.ManyToManyField(
        Symptom, related_name="%(class)ss", blank=True)
    references = models.ManyToManyField(
        'Term', related_name="%(class)ss", blank=True)
    video = EmbedVideoField(blank=True)

    LOW = 'LOW'
    MIDDLE = 'MIDDLE'
    HIGH = 'HIGH'
    UNDER_MIDDLE = 'UNDER_MIDDLE'
    OVER_MIDDLE = 'OVER_MIDDLE'
    ANY = 'ANY'

    STAMINA_CHOICES = [
        (LOW, 'Low'),
        (MIDDLE, 'Middle'),
        (HIGH, 'High'),
        (UNDER_MIDDLE, 'Under Middle'),
        (OVER_MIDDLE, 'Over Middle'),
        (ANY, 'Any')
    ]

    stamina = models.CharField(max_length=64,
                               choices=STAMINA_CHOICES, blank=True)
    target = models.CharField(max_length=256, blank=True, null=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        if self.name_en:
            return "{0} - {1}".format(self.name, self.name_en)
        else:
            return self.name

    # allow images to be shown on the admin page
    def admin_image(self):
        if self.image:
            return mark_safe('<img src="{}" style="width:100px; height:auto;">'.format(self.image.url))
        else:
            return 'no image'
    admin_image.allow_tags = True

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        ordering = ['name']


class IngredientImage(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='ingredient_images')
    image = models.ImageField(upload_to=get_image_path)
    created_at = models.DateField(auto_now_add=True)
    caption = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return "{id}. {name} [{date}]".format(
            id=str(self.id),
            name=self.ingredient.name,
            date=str(self.created_at)
        )

    class Meta:
        verbose_name = 'Ingredient Image'
        verbose_name_plural = 'Ingredient Images'


class RelatedMedicine(models.Model):
    base = models.ForeignKey(
        'Medicine', on_delete=models.CASCADE, related_name='base')
    related = models.ForeignKey(
        'Medicine', on_delete=models.CASCADE, related_name='related')

    def __str__(self):
        return "{id}. {related} - {base}".format(
            id=str(self.id),
            related=self.related.name,
            base=self.base.name
        )

    class Meta:
        verbose_name = 'Related Medicine'
        verbose_name_plural = 'Related Medicines'

        # NOTE: making A-B and B-A combination treated as the same to prevent duplication.
        # Doesn't matter which one goes to which in terms of mutuality
        constraints = [
            models.UniqueConstraint(
                fields=['base', 'related'], name='unique_related'),
        ]

    # override methods for mutual relationships
    # NOTE: when A-B relationship is built/deleted, so is B-A.
    def save(self, *args, **kwargs):
        self.related.relationships.add(self.base)
        super(RelatedMedicine, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.related.relationships.remove(self.base)
        super(RelatedMedicine, self).delete(*args, **kwargs)


class Medicine(models.Model):
    name = models.CharField(max_length=128)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    publisher = models.CharField(max_length=64, blank=True, null=True)
    effects = models.ManyToManyField(
        Effect, related_name="%(class)ss", blank=True)
    video = EmbedVideoField(blank=True)

    FIRST = '1'
    D_SECOND = 'D2'
    SECOND = '2'
    THIRD = '3'
    D_QUASI = 'DQ'
    QUASI = 'Q'
    PRESCRIPTION = 'P'
    COSMETICS = 'C'
    INSTRUCTION = 'I'
    ANIMAL = 'A'

    CLASSIFICATION_CHOICES = [
        (FIRST, 'First-class'),
        (D_SECOND, 'Designated second-class'),
        (SECOND, 'Second-class'),
        (THIRD, 'Third-class'),
        (D_QUASI, 'Designated quasi-drugs'),
        (QUASI, 'Quasi-drugs'),
        (PRESCRIPTION, 'Prescription drugs'),
        (COSMETICS, 'Cosmetics'),
        (INSTRUCTION, 'Instruction'),
        (ANIMAL, 'Animal')
    ]

    classification = models.CharField(max_length=64,
                                      choices=CLASSIFICATION_CHOICES, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="%(class)ss", null=True, blank=True)

    relationships = models.ManyToManyField(
        'self', verbose_name="Related Medicines", blank=True, symmetrical=False, related_name='related_%(class)ss', through='RelatedMedicine')
    ingredients = models.ManyToManyField(
        Ingredient, related_name="%(class)ss", blank=True)
    link = models.CharField(max_length=256, null=True, blank=True)
    prohibitions = models.ManyToManyField(
        Precaution, related_name="prohibition_%(class)ss", blank=True)
    consultations = models.ManyToManyField(
        Precaution, related_name="consultation_%(class)ss", blank=True)
    symptoms = models.ManyToManyField(
        Symptom, related_name="%(class)ss", blank=True)

    def __str__(self):
        if self.publisher:
            return "{id}. {name} - {publisher}".format(
                id=str(self.id),
                name=self.name,
                publisher=self.publisher
            )
        else:
            return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Medicine'
        verbose_name_plural = 'Medicines'
        ordering = ('name',)


class MedicineImage(models.Model):
    medicine = models.ForeignKey(
        Medicine, on_delete=models.CASCADE, related_name='medicine_images')
    image = models.ImageField(upload_to=get_image_path)
    created_at = models.DateField(auto_now_add=True)
    caption = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return "{id}. {name} [{date}]".format(
            id=str(self.id),
            name=self.medicine.name,
            date=str(self.created_at)
        )

    class Meta:
        verbose_name = 'Medicine Image'
        verbose_name_plural = 'Medicine Images'


class Term(models.Model):
    name = models.CharField(max_length=128)
    name_en = models.CharField(max_length=128, null=True, blank=True)
    alias = models.CharField(max_length=128, null=True, blank=True)
    products = models.ManyToManyField(
        Medicine, related_name="%(class)ss",  blank=True)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    relationships = models.ManyToManyField(
        'self', blank=True)
    video = EmbedVideoField(blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.PROTECT, blank=True, null=True, related_name='child_terms')

    ORGAN = 'ORGAN'
    CHEMICAL = 'CHEMICAL'
    FUNCTION = 'FUNCTION'

    CLASSIFICATION_CHOICES = [
        (ORGAN, 'Organ'),
        (CHEMICAL, 'Chemical'),
        (FUNCTION, 'Function'),
    ]
    classification = models.CharField(max_length=32,
                                      choices=CLASSIFICATION_CHOICES, blank=True, null=True)

    def __str__(self):
        return "{id}. {jp} - {en}".format(
            id=str(self.id),
            jp=self.name,
            en=self.name_en
        )

    class Meta:
        verbose_name = 'Term'
        verbose_name_plural = 'Terms'
        ordering = ['name']


class TermImage(models.Model):
    term = models.ForeignKey(
        Term, on_delete=models.CASCADE, related_name='term_images')
    image = models.ImageField(upload_to=get_image_path)
    created_at = models.DateField(auto_now_add=True)
    caption = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return "{id}. {name} [{date}]".format(
            id=str(self.id),
            name=self.term.name,
            date=str(self.created_at)
        )

    class Meta:
        verbose_name = 'Term Image'
        verbose_name_plural = 'Term Images'


class Intake(models.Model):
    medicine = models.ForeignKey(
        Medicine, on_delete=models.PROTECT,  blank=True, null=True)
    taken_at = models.DateField(default=date.today)
    amount = models.IntegerField(blank=True, null=True)
    unit = models.CharField(max_length=128, blank=True, null=True)
    time = models.CharField(max_length=128, blank=True, null=True)
    reason = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Intake'
        verbose_name_plural = 'Intakes'


class Document(models.Model):
    name = models.CharField(max_length=128)
    name_en = models.CharField(max_length=128, null=True, blank=True)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'


class Law(models.Model):
    name = models.CharField(max_length=128)
    link = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Law'
        verbose_name_plural = 'Laws'


class Article(models.Model):
    law = models.ForeignKey(
        Law, on_delete=models.PROTECT)
    name = models.CharField(max_length=128)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    relationships = models.ManyToManyField(
        'self', blank=True)
    body = models.TextField(null=False)
    memo = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{id}. {name} - [{law}]".format(
            id=str(self.id),
            name=self.name,
            law=self.law.name[:40]
        )

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'


# Class that contains images attached to every models
# TODO: comtemplate if this is more suitable rather than creating relating Image models one by one.

class ReferenceImage(models.Model):
    medicine = models.ForeignKey(
        Medicine, on_delete=models.CASCADE, related_name='medicine_references', blank=True, null=True)
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='ingredient_references', blank=True, null=True)
    term = models.ForeignKey(
        Term, on_delete=models.CASCADE, related_name='term_references', blank=True, null=True)
    disease = models.ForeignKey(
        Disease, on_delete=models.CASCADE, related_name='disease_references', blank=True, null=True)
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='property_references', blank=True, null=True)
    symptom = models.ForeignKey(
        Symptom, on_delete=models.CASCADE, related_name='symptom_references', blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path)
    created_at = models.DateField(auto_now_add=True)
    caption = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        # return the right caption attached to an image.
        def showObjectName(i):
            while i < len(attr_list):
                target = getattr(self, attr_list[i])
                if target:
                    return "{id}. {name}".format(
                        id=getattr(target, 'id'),
                        name=getattr(target, 'name')
                    )
                elif target is None:
                    i += 1
                else:
                    return 'Something went wrong while populating the data'

        return showObjectName(0)

    class Meta:
        verbose_name = 'Reference Image'
        verbose_name_plural = 'Reference Images'

    # set validation to assure only one value is assigned.
    def clean(self):
        key_list = [
            self.medicine,
            self.ingredient,
            self.term,
            self.disease,
            self.property,
            self.symptom,
        ]
        if key_list.count(None) < len(key_list) - 1:
            raise ValidationError(
                'Only 1 ForegnKey is allowed.')
        elif key_list.count(None) == len(key_list):
            raise ValidationError(
                'No ForeignKey is selected. ')
        else:
            return 'Validation failed. Need to fix this exception right away.'
