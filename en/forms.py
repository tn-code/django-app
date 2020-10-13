from django import forms
from .models import Term, Definition, Synonym, Sentence, Collocation, Derivative, Dialect, Clause
from django.db.models.functions import Lower
from django.forms.models import BaseInlineFormSet

CollocationFormset = forms.inlineformset_factory(
    Definition, Collocation, fields='__all__', can_delete=False, extra=1, exclude=('comment', 'sentences', 'translation', 'term'))

ClauseFormset = forms.inlineformset_factory(
    Definition, Clause, fields='__all__', can_delete=False, extra=1, )


class BaseDefinitionFormset(BaseInlineFormSet):
    def add_fields(self, form, index):
        super(BaseDefinitionFormset, self).add_fields(form, index)

        # save the formset in the 'nested' property
        form.nested = [

            CollocationFormset(
                instance=form.instance,
                data=form.data if form.is_bound else None,
                files=form.files if form.is_bound else None,
                prefix='collocation-%s-%s' % (
                    form.prefix,
                    CollocationFormset.get_default_prefix())),


            ClauseFormset(
                instance=form.instance,
                data=form.data if form.is_bound else None,
                files=form.files if form.is_bound else None,
                prefix='clause-%s-%s' % (
                    form.prefix,
                    ClauseFormset.get_default_prefix())),

        ]

    def is_valid(self):
        result = super(BaseDefinitionFormset, self).is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    for n in form.nested:
                        # make sure each nested formset is valid as well
                        result = result and n.is_valid()

        return result

    def save(self, commit=True):

        result = super(BaseDefinitionFormset, self).save(commit=commit)

        for form in self.forms:
            if hasattr(form, 'nested'):
                for n in form.nested:
                    if not self._should_delete_form(form):
                        n.save(commit=commit)

        return result


class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = '__all__'
        exclude = ('synonyms', 'derivatives', 'reviewed_at', 'genres',
                   'occasions', 'proficiency')
        can_delete = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    DefinitionFormset = forms.inlineformset_factory(
        Term, Definition, formset=BaseDefinitionFormset, fields='__all__',
        extra=3, can_delete=False
    )

    SentenceFormset = forms.inlineformset_factory(
        Term, Sentence, fields='__all__',
        extra=2, exclude=('memo', 'template', 'is_generic'), can_delete=False
    )
    CollocationFormset = forms.inlineformset_factory(
        Definition, Collocation, fields='__all__',
        extra=4, can_delete=False
    )
    ClauseFormset = forms.inlineformset_factory(
        Definition, Clause, fields='__all__',
        extra=2, can_delete=False
    )
    DerivativeFormset = forms.inlineformset_factory(
        Term, Derivative, fk_name='derivative', fields='__all__',
        extra=1, can_delete=False
    )

    SynonymFormset = forms.inlineformset_factory(
        Term, Synonym, fk_name='from_term', fields='__all__',
        extra=3, exclude=('is_paraphrase',), can_delete=False
    )

    # NOTE: Implementation of Synonym formset comes with ValueError: 'en.Synonym' has more than one ForeignKey to 'en.Term' as it is an intermediate table.


class SentenceForm(forms.ModelForm):
    class Meta:
        model = Sentence
        fields = '__all__'
        can_delete = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['term'].queryset = Term.objects.all().order_by(
            Lower('name'))


class SynonymForm(forms.ModelForm):
    class Meta:
        model = Synonym
        fields = '__all__'
        can_delete = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['from_term'].queryset = Term.objects.all().order_by(
            Lower('name'))
        self.fields['to_term'].queryset = Term.objects.all().order_by(
            Lower('name'))
