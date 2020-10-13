import os
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import date
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower


def get_image_path(self, filename):
    if self.__class__.__name__ == 'Sentence':
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
    else:
        if hasattr(self, 'name'):
            return os.path.join('images', 'en', self.__class__.__name__, self.name, filename)
        elif hasattr(self, 'speaker'):
            return os.path.join('images', 'en', self.__class__.__name__, self.speaker, filename)
        elif hasattr(self, 'title'):
            return os.path.join('images', 'en', self.__class__.__name__, str(self.id), filename)
        else:
            return 'Error occured while setting an image path'


class Dialect(models.Model):
    name = models.CharField(max_length=64)
    image = models.ImageField(upload_to=get_image_path, blank=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Dialect'
        verbose_name_plural = 'Dialects'


class Grammar(models.Model):
    name = models.CharField(max_length=256)
    body = models.TextField()

    def __str__(self):
        return str(self.id) + '. ' + self.body

    class Meta:
        verbose_name = 'Grammar'
        verbose_name_plural = 'Grammars'


class Usage(models.Model):
    title = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Title")
    body = models.TextField()

    grammar = models.ForeignKey(
        Grammar, on_delete=models.PROTECT, blank=True, null=True)
    source_name = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Source")

    WEBSITE = 'WEBSITE'
    BOOK = 'BOOK'
    YOUTUBE = 'YOUTUBE'
    MOVIE = 'MOVIE'
    PODCAST = 'PODCAST'
    LYRICS = 'LYRICS'
    NEWS = 'NEWS'
    GAME = 'GAME'

    MEDIA_CHOICES = [
        (WEBSITE, 'Website'),
        (BOOK, 'Book'),
        (YOUTUBE, 'YouTube'),
        (MOVIE, 'Movie'),
        (PODCAST, 'Podcast'),
        (LYRICS, 'Lyrics'),
        (NEWS, 'News'),
        (GAME, 'Game')
    ]
    source_media = models.CharField(max_length=32,
                                    choices=MEDIA_CHOICES, blank=True, null=True, verbose_name="Media Type")
    source_link = models.TextField(
        blank=True, null=True, verbose_name="Source Link")
    reference = models.ImageField(upload_to=get_image_path, blank=True)

    def __str__(self):
        if self.title != None:
            return str(self.id) + '. ' + self.title
        else:
            return str(self.id) + '. ' + self.body

    class Meta:
        verbose_name = 'Usage'
    verbose_name_plural = 'Usages'


class Genre(models.Model):
    name = models.CharField(max_length=128)
    image = models.ImageField(upload_to=get_image_path, blank=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'


class Occasion(models.Model):
    name = models.CharField(max_length=128)
    image = models.ImageField(upload_to=get_image_path, blank=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Occasion'
        verbose_name_plural = 'Occasions'


class Term(models.Model):
    name = models.CharField(max_length=128, unique=True)
    pronunciation = models.CharField(max_length=128, blank=True, null=True)

    synonyms = models.ManyToManyField(
        'self', verbose_name="Synonyms", blank=True, symmetrical=False, related_name='%(class)ss_related', through='Synonym')
    derivatives = models.ManyToManyField(
        'self', verbose_name="Derivatives", blank=True, symmetrical=False, related_name='derived_%(class)ss', through='Derivative')
    dialects = models.ManyToManyField(
        Dialect, blank=True, symmetrical=False, related_name='%(class)ss', verbose_name="Regional & Dialects")
    usages = models.ManyToManyField(
        Usage, blank=True, symmetrical=False, related_name='%(class)ss', verbose_name="Usages")
    conjugation = models.CharField(max_length=256, blank=True, null=True)

    memo = models.TextField(blank=True, null=True, verbose_name="Sidenote")
    is_basic = models.BooleanField(default=False, verbose_name="Basic")
    is_advanced = models.BooleanField(default=False, verbose_name="Advanced")
    is_onomatopea = models.BooleanField(
        default=False, verbose_name="Onomatopea")
    is_pronunciation = models.BooleanField(
        default=False, verbose_name="Pronunciation")

    image = models.ImageField(upload_to=get_image_path, blank=True)
    reviewed_at = models.DateField(blank=True, null=True)
    occasions = models.ManyToManyField(
        Occasion, related_name='%(class)ss', blank=True)
    genres = models.ManyToManyField(
        Genre, related_name='%(class)ss', blank=True)
    alternatives = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    proficiency = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)

    WORD = 'WORD'
    PHRASE = 'PHRASE'
    PHRASAL_VERB = 'PHRASAL_VERB'
    COMPOUND = 'COMPOUND'
    TEMPLATE = 'TEMPLATE'
    LOANWORD = 'LOANWORD'
    AFFIX = 'AFFIX'

    TYPE_CHOICES = [
        (WORD, 'Word'),
        (PHRASE, 'Phrase'),
        (PHRASAL_VERB, 'Phrasal Verb'),
        (COMPOUND, 'Compound'),
        (TEMPLATE, 'Template'),
        (LOANWORD, 'Loanword'),
        (AFFIX, 'AFFIX'),
    ]
    type = models.CharField(max_length=32,
                            choices=TYPE_CHOICES, blank=True, null=True, verbose_name="Type")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Term'
        verbose_name_plural = 'Terms'
        ordering = [Lower('name')]


class Sentence(models.Model):
    term = models.ForeignKey(
        Term, on_delete=models.PROTECT, related_name='%(class)ss_related', blank=True, null=True)

    body = models.TextField()
    source_name = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Source")
    is_generic = models.BooleanField(
        default=False, blank=True, null=True, verbose_name="Generic Sentence")

    WEBSITE = 'WEBSITE'
    BOOK = 'BOOK'
    YOUTUBE = 'YOUTUBE'
    MOVIE = 'MOVIE'
    PODCAST = 'PODCAST'
    LYRICS = 'LYRICS'
    NEWS = 'NEWS'
    GAME = 'GAME'
    PRODUCT = 'PRODUCT'
    EMAIL = 'EMAIL'

    MEDIA_CHOICES = [
        (WEBSITE, 'Website'),
        (BOOK, 'Book'),
        (YOUTUBE, 'YouTube'),
        (MOVIE, 'Movie'),
        (PODCAST, 'Podcast'),
        (LYRICS, 'Lyrics'),
        (NEWS, 'News'),
        (GAME, 'Game'),
        (PRODUCT, 'Product'),
        (EMAIL, 'Email')
    ]
    source_media = models.CharField(max_length=32,
                                    choices=MEDIA_CHOICES, blank=True, null=True, verbose_name="Media Type")
    source_link = models.TextField(
        blank=True, null=True, verbose_name="Source Link")
    memo = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    occasions = models.ManyToManyField(
        Occasion, related_name='%(class)ss', blank=True)
    genres = models.ManyToManyField(
        Genre, related_name='%(class)ss', blank=True)
    grammar = models.ForeignKey(
        Grammar, on_delete=models.PROTECT, blank=True, null=True)
    usage = models.ForeignKey(
        Usage, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        if self.is_generic == False or self.is_generic is None:

            return str(self.id) + '. ' + self.body[:30] + ' － ' + str(self.term.name)

        else:
            return str(self.id) + '. ' + self.body[:30] + ' － [GENERIC]'

    class Meta:
        verbose_name = 'Sentence'
        verbose_name_plural = 'Sentences'

    def clean(self):
        if self.is_generic == True and self.term is not None:
            raise ValidationError(
                'No terms allowed assignment with the "is_generic" field checked.')


class Synonym(models.Model):
    from_term = models.ForeignKey(
        Term, on_delete=models.CASCADE, related_name='from_term')
    to_term = models.ForeignKey(
        Term, on_delete=models.CASCADE, related_name='to_term')

    is_paraphrase = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + '. ' + self.from_term.name + '－' + self.to_term.name

    class Meta:
        verbose_name = 'Synonym'
        verbose_name_plural = 'Synonyms'
        constraints = [
            models.UniqueConstraint(
                fields=['from_term', 'to_term'], name='unique_synonyms_from'),
            models.UniqueConstraint(
                fields=['to_term', 'from_term'], name='unique_synonyms_to'),
        ]

    def save(self, *args, **kwargs):
        self.to_term.synonyms.add(self.from_term)
        super(Synonym, self).save(*args, **kwargs)


class Derivative(models.Model):
    base = models.ForeignKey(
        Term, on_delete=models.CASCADE, related_name='base')
    derivative = models.ForeignKey(
        Term, on_delete=models.CASCADE, related_name='derivative')

    NOUN = 'NOUN'
    ADJECTIVE = 'ADJECTIVE'
    ADVERB = 'ADVERB'
    VERB = 'VERB'
    PHRASE = 'PHRASE'

    POS_CHOICES = [
        (NOUN, 'Noun'),
        (ADJECTIVE, 'Adjective'),
        (ADVERB, 'Adverb'),
        (VERB, 'Verb'),
        (PHRASE, 'Phrase')
    ]
    PoS = models.CharField(
        max_length=32, choices=POS_CHOICES, default=NOUN, verbose_name="Part of Speech")

    def __str__(self):
        return str(self.id) + '. ' + self.derivative.name + '－' + self.base.name

    class Meta:
        verbose_name = 'Derivative'
        verbose_name_plural = 'Derivatives'
        constraints = [
            models.UniqueConstraint(
                fields=['base', 'derivative'], name='unique_derivatives'),
        ]


class Definition(models.Model):
    definition = models.CharField(max_length=256)
    translation = models.CharField(max_length=256, blank=True, null=True)
    term = models.ForeignKey(
        Term, on_delete=models.CASCADE, blank=True, null=True)
    pronunciation = models.CharField(max_length=128, blank=True, null=True)

    comment = models.TextField(blank=True, null=True)
    ADJECTIVE = 'ADJECTIVE'
    ADVERB = 'ADVERB'
    VERB = 'VERB'
    PREPOSITION = 'PREPOSITION'
    NOUN = 'NOUN'
    CONJUNCTION = 'CONJUNCTION'
    AUXILIARY = 'AUXILIARY'
    PHRASE = 'PHRASE'

    POS_CHOICES = [
        (ADJECTIVE, 'Adjective'),
        (ADVERB, 'Adverb'),
        (VERB, 'Verb'),
        (PREPOSITION, 'Preposition'),
        (NOUN, 'Noun'),
        (PHRASE, 'PHRASE'),
        (CONJUNCTION, 'Conjunction'),
        (AUXILIARY, 'Auxiliary'),
    ]
    PoS = models.CharField(
        max_length=32, choices=POS_CHOICES, blank=True, null=True, verbose_name="Part of Speech")

    NORMAL = 'NORMAL'
    FORMAL = 'FORMAL'
    INFORMAL = 'INFORMAL'
    LITERARY = 'LITERARY'
    OLD_FASHIONED = 'OLD_FASHIONED'

    FORMALITY_CHOICES = [
        (NORMAL, 'Normal'),
        (FORMAL, 'Formal'),
        (INFORMAL, 'Informal'),
        (LITERARY, 'Literary'),
        (OLD_FASHIONED, 'Old-fashioned'),

    ]
    formality = models.CharField(
        max_length=32, choices=FORMALITY_CHOICES, default=NORMAL)
    dialects = models.ManyToManyField(
        Dialect, blank=True, symmetrical=False, related_name='%(class)ss', verbose_name="Regional & Dialects")

    is_uncountable = models.BooleanField(
        blank=True, null=True, verbose_name="Uncountable Noun")
    unit = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.definition[:20] + ' － ' + self.term.name

    class Meta:
        verbose_name = 'Definition'
        verbose_name_plural = 'Definitions'

    def clean(self):
        if self.PoS != 'NOUN' and self.is_uncountable == True:
            raise ValidationError(
                'The part of speech of the term must be a noun e when checking the field "is_uncountable"')


class Clause(models.Model):
    definition = models.ForeignKey(
        Definition, on_delete=models.CASCADE)

    INFINITIVE = 'INFINITIVE'
    GERUND = 'GERUND'
    THAT = 'THAT'
    INTERROGATIVE = 'INTERROGATIVE'
    IF = 'IF'
    AUXILIARY = 'AUXILIARY'

    CLAUSE_CHOICES = [
        (AUXILIARY, 'Auxiliary'),
        (INFINITIVE, 'Infinitive'),
        (GERUND, 'Gerund'),
        (THAT, 'That'),
        (INTERROGATIVE, 'Interrogative'),
    ]

    clause = models.CharField(
        max_length=32, choices=CLAUSE_CHOICES, default=INFINITIVE, verbose_name="Clause Type")

    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return '{id}. {term} － [{clause}]'.format(
            id=self.id,
            term=self.definition.term.name,
            clause=self.clause
        )

    class Meta:
        verbose_name = 'Clause'
        verbose_name_plural = 'Clauses'


class Collocation(models.Model):
    name = models.CharField(max_length=128, verbose_name="Words")

    PREPOSITION = 'PREPOSITION'
    NOUN = 'NOUN'
    VERB = 'VERB'
    ADJECTIVE = 'ADJECTIVE'
    ADVERB = 'ADVERB'
    CONJUNCTION = 'CONJUNCTION'

    POS_CHOICES = [
        (ADJECTIVE, 'Adjective'),
        (ADVERB, 'Adverb'),
        (VERB, 'Verb'),
        (PREPOSITION, 'Preposition'),
        (NOUN, 'Noun'),
        (CONJUNCTION, 'Conjunction'),

    ]
    PoS = models.CharField(
        max_length=32, choices=POS_CHOICES, default=NOUN, verbose_name="Part of Speech")

    definition = models.ForeignKey(
        Definition, on_delete=models.CASCADE)
    sentences = models.ManyToManyField(
        Sentence, blank=True, symmetrical=False, related_name='%(class)ss_related')
    translation = models.CharField(max_length=256, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return '{id}. {term} － [{name}]'.format(
            id=self.id,
            term=self.definition.term.name,
            name=self.name
        )

    class Meta:
        verbose_name = 'Collocation'
        verbose_name_plural = 'Collocations'


class Comparison(models.Model):
    name = models.CharField(max_length=256, default='No Title')
    term_1 = models.ForeignKey(
        Term, on_delete=models.PROTECT, related_name='term_1_related')
    term_1_description = models.TextField(blank=True, null=True)
    term_2 = models.ForeignKey(
        Term, on_delete=models.PROTECT, related_name='term_2_related')

    term_2_description = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    sentences = models.ManyToManyField(
        Sentence, blank=True, symmetrical=False, related_name='%(class)ss_related')

    def __str__(self):
        return str(self.id) + '. ' + self.name

    class Meta:
        verbose_name = 'Comparison'
        verbose_name_plural = 'Comparisons'


class Dialogue(models.Model):
    name = models.CharField(max_length=256, default='No Title')
    source_name = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Source")

    WEBSITE = 'WEBSITE'
    BOOK = 'BOOK'
    YOUTUBE = 'YOUTUBE'
    MOVIE = 'MOVIE'
    PODCAST = 'PODCAST'
    NEWS = 'NEWS'
    GAME = 'GAME'

    MEDIA_CHOICES = [
        (WEBSITE, 'Website'),
        (BOOK, 'Book'),
        (YOUTUBE, 'YouTube'),
        (MOVIE, 'Movie'),
        (PODCAST, 'Podcast'),
        (NEWS, 'News'),
        (GAME, 'Game')
    ]
    source_media = models.CharField(max_length=32,
                                    choices=MEDIA_CHOICES, blank=True, null=True, verbose_name="Media Type")
    source_link = models.TextField(
        blank=True, null=True, verbose_name="Source Link")
    occasion = models.ForeignKey(
        Occasion, on_delete=models.PROTECT, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name + ' － ' + self.source_name

    class Meta:
        verbose_name = 'Dialogue'
        verbose_name_plural = 'Dialogues'


class Line(models.Model):
    speaker = models.CharField(max_length=32, null=True, blank=True)
    body = models.CharField(max_length=512)
    dialogue = models.ForeignKey(Dialogue, on_delete=models.PROTECT)
    order = models.IntegerField(default=1)
    image = models.ImageField(upload_to=get_image_path, null=True, blank=True)

    def __str__(self):
        return str(self.id) + '. ' + self.dialogue.name + '[' + str(self.order) + '] ' + self.body[:20]

    class Meta:
        verbose_name = 'Line'
        verbose_name_plural = 'Lines'
