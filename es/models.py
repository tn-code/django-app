import os
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import date
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower


def get_image_path(self, filename):
    if hasattr(self, 'name'):
        return os.path.join('images', 'en', self.__class__.__name__, self.name, filename)
    elif hasattr(self, 'title'):
        return os.path.join('images', 'en', self.__class__.__name__, str(self.id), filename)
    else:
        if self.is_generic == True:
            return os.path.join('images', 'en', self.__class__.__name__, "generic", str(self.id), filename)
        else:
            # For sentences for terms
            if hasattr(self, 'term') and self.term is not None:
                return os.path.join('images', 'en', self.__class__.__name__, self.term.name, str(self.id), filename)
            # For sentences for templates
            elif hasattr(self, 'template') and self.template is not None:
                return os.path.join('images', 'en', self.__class__.__name__, self.template.name, str(self.id), filename)
            else:
                raise ValidationError(
                    'Something went wrong while uploading the image.')


class Usage(models.Model):
    title = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Título")
    body = models.TextField()
    source_name = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Fuente")

    WEBSITE = 'WEBSITE'
    BOOK = 'BOOK'
    YOUTUBE = 'YOUTUBE'
    PODCAST = 'PODCAST'
    LYRICS = 'LYRICS'

    MEDIA_CHOICES = [
        (WEBSITE, 'Sitio Web'),
        (BOOK, 'Libro'),
        (YOUTUBE, 'YouTube'),
        (PODCAST, 'Podcast'),
        (LYRICS, 'Letra'),
    ]

    source_media = models.CharField(max_length=32,
                                    choices=MEDIA_CHOICES, blank=True, null=True, verbose_name="Tipo de Media")
    source_link = models.TextField(
        blank=True, null=True, verbose_name="Enlace de Fuente")
    reference = models.ImageField(upload_to=get_image_path, blank=True)

    def __str__(self):
        if self.title != None:
            return str(self.id) + '. ' + self.title
        else:
            return str(self.id) + '. ' + self.body

    class Meta:
        verbose_name = 'Uso'
        verbose_name_plural = 'Usos'


class Term(models.Model):
    name = models.CharField(max_length=128, verbose_name="Nombre")
    pronunciation = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Pronunciación")
    usages = models.ManyToManyField(
        Usage, blank=True, symmetrical=False, related_name='%(class)ss', verbose_name="Usos")

    MASCULINE = 'MASCULINE'
    FEMININE = 'FEMININE'

    GENDER_CHOICES = [
        (MASCULINE, 'Masculino'),
        (FEMININE, 'Femenino'),
    ]
    gender = models.CharField(
        max_length=32, choices=GENDER_CHOICES, null=True, blank=True, verbose_name='Género')

    infinitive = models.ForeignKey(
        'self', on_delete=models.PROTECT, verbose_name="Infinitivo", blank=True, null=True)

    FIRST_S = 'FIRST_S'
    SECOND_S = 'SECOND_S'
    THIRD_S = 'THIRD_S'
    FIRST_P = 'FIRST_P'
    SECOND_P = 'SECOND_P'
    THIRD_P = 'THIRD_P'

    PERSONA_CHOICES = [
        (FIRST_S, 'Primera Persona del Singular'),
        (SECOND_S, 'Segunda Persona del Singular'),
        (THIRD_S, 'Tercera Persona del Singular'),
        (FIRST_P, 'Primera Persona del Plural'),
        (SECOND_P, 'Segunda Persona del Plural'),
        (THIRD_P, 'Tercera Persona del Plural'),
    ]
    persona = models.CharField(max_length=32,
                               choices=PERSONA_CHOICES, blank=True, null=True, verbose_name="Persona")

    INDICATIVE = 'INDICATIVE'
    SUBJUNCTIVE = 'SUBJUNCTIVE'
    IMPERATIVE = 'IMPERATIVE'

    MOOD_CHOICES = [
        (INDICATIVE, 'Indicativo'),
        (SUBJUNCTIVE, 'Subjunctivo'),
        (IMPERATIVE, 'Imperativo'),
    ]
    mood = models.CharField(max_length=32,
                            choices=MOOD_CHOICES, blank=True, null=True, verbose_name="Modo")

    PRESENT = 'PRESENT'
    PRETERITE = 'PRETERITE'
    IMPERFECT = 'INPERFECT'
    FUTURE = 'FUTURE'
    CONDITIONAL = 'CONDITIONAL'
    AFFIRMATIVE = 'AFFIRMATIVE'
    NEGATIVE = 'NEGATIVE'

    TENSE_CHOICES = [
        (PRESENT, 'Presente'),
        (PRETERITE, 'Pretérito'),
        (IMPERFECT, 'Imperfecto'),
        (FUTURE, 'Futuro'),
        (CONDITIONAL, 'Condicional'),
        (AFFIRMATIVE, 'Affirmative'),
        (NEGATIVE, 'Negative'),
    ]
    tense = models.CharField(max_length=32,
                             choices=TENSE_CHOICES, blank=True, null=True, verbose_name="Tiempo")
    memo = models.TextField(blank=True, null=True, verbose_name="Nota")
    image = models.ImageField(upload_to=get_image_path,
                              blank=True, verbose_name="Imagen")
    reviewed_at = models.DateField(
        blank=True, null=True, verbose_name="Revisado en")
    created_at = models.DateField(auto_now_add=True, verbose_name="Creado en")
    proficiency = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], default=0, verbose_name="Competencia")

    WORD = 'WORD'
    PHRASE = 'PHRASE'
    TEMPLATE = 'TEMPLATE'

    TYPE_CHOICES = [
        (WORD, 'Parabra'),
        (PHRASE, 'Frase'),
        (TEMPLATE, 'Plantilla'),
    ]
    type = models.CharField(max_length=32,
                            choices=TYPE_CHOICES, blank=True, null=True, verbose_name="Tipo")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Termino'
        verbose_name_plural = 'Terminos'
        ordering = [Lower('name')]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'gender'], name='unique_name_gender'),
            models.UniqueConstraint(
                fields=['name', 'persona', 'mood', 'tense'], name='unique_conjugation'),
        ]


class Sentence(models.Model):
    term = models.ForeignKey(
        Term, on_delete=models.PROTECT, related_name='%(class)ss', blank=True, null=True)

    body = models.TextField(verbose_name="Cuerpo")
    source_name = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Fuente")
    is_generic = models.BooleanField(
        default=False, blank=True, null=True, verbose_name="Oración genérica")

    WEBSITE = 'WEBSITE'
    BOOK = 'BOOK'
    YOUTUBE = 'YOUTUBE'
    PODCAST = 'PODCAST'
    LYRICS = 'LYRICS'

    MEDIA_CHOICES = [
        (WEBSITE, 'Sitio Web'),
        (BOOK, 'Libro'),
        (YOUTUBE, 'YouTube'),
        (PODCAST, 'Podcast'),
        (LYRICS, 'Letra'),
    ]
    source_media = models.CharField(max_length=32,
                                    choices=MEDIA_CHOICES, blank=True, null=True, verbose_name="Tipo de Media")
    source_link = models.TextField(
        blank=True, null=True, verbose_name="Enlace de Fuente")
    memo = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path,
                              null=True, blank=True, verbose_name="Imagen")
    usage = models.ForeignKey(
        Usage, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        if self.is_generic == False or self.is_generic is None:

            return str(self.id) + '. ' + self.body[:30] + ' － ' + str(self.term.name)

        else:
            return str(self.id) + '. ' + self.body[:30] + ' － [GENERIC]'

    class Meta:
        verbose_name = 'Oración'
        verbose_name_plural = 'Oraciónes'

    def clean(self):
        if self.is_generic == True and self.term is not None:
            raise ValidationError(
                'No terms allowed assignment with the "is_generic" field checked.')


class Definition(models.Model):
    definition = models.CharField(max_length=256, verbose_name="Definición")
    translation = models.CharField(
        max_length=256, blank=True, null=True, verbose_name="Traducción")
    term = models.ForeignKey(
        Term, on_delete=models.CASCADE, blank=True, null=True)
    comment = models.TextField(blank=True, null=True, verbose_name="Nota")

    NOUN = 'NOUN'
    VERB = 'VERB'
    ADJECTIVE = 'ADJECTIVE'
    ADVERB = 'ADVERB'
    PREPOSITION = 'PREPOSITION'
    CONJUNCTION = 'CONJUNCTION'
    ARTICLE = 'ARTICLE'
    PRONOUN = 'Pronoun'
    INTERJECTION = 'INTERJECTION'
    PHRASE = 'PHRASE'

    POS_CHOICES = [
        (NOUN, 'Sustantivo'),
        (VERB, 'Verbo'),
        (ADJECTIVE, 'Adjetivo'),
        (ADVERB, 'Adverbio'),
        (PREPOSITION, 'Preposición'),
        (CONJUNCTION, 'Conjunción'),
        (ARTICLE, 'Articulo'),
        (PRONOUN, 'Pronombre'),
        (INTERJECTION, 'Interjección'),
        (PHRASE, 'Frase'),

    ]
    PoS = models.CharField(
        max_length=32, choices=POS_CHOICES, blank=True, null=True, verbose_name="Parte de Oración")

    NORMAL = 'NORMAL'
    FORMAL = 'FORMAL'
    INFORMAL = 'INFORMAL'

    FORMALITY_CHOICES = [
        (NORMAL, 'Normal'),
        (FORMAL, 'Formal'),
        (INFORMAL, 'Informal'),
    ]
    formality = models.CharField(
        max_length=32, choices=FORMALITY_CHOICES, default=NORMAL, verbose_name="Formalidad")

    def __str__(self):
        return str(self.id) + '. ' + self.definition[:20] + ' － ' + self.term.name

    class Meta:
        verbose_name = 'Definición'
        verbose_name_plural = 'Definiciónes'
