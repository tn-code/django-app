from django import forms
from .models import Term, Definition, Sentence
from django.db.models.functions import Lower
from django.forms.models import BaseInlineFormSet


class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = '__all__'
        exclude = ('infinitive', 'reviewed_at', 'proficiency')
        can_delete = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    DefinitionFormset = forms.inlineformset_factory(
        Term, Definition, fields='__all__',
        extra=1, can_delete=False
    )

    SentenceFormset = forms.inlineformset_factory(
        Term, Sentence, fields='__all__',
        extra=1, exclude=('usage', 'memo', 'template', 'is_generic'), can_delete=False
    )


class SentenceForm(forms.ModelForm):
    class Meta:
        model = Sentence
        fields = '__all__'
        can_delete = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['term'].queryset = Term.objects.all().order_by(
            Lower('name'))
