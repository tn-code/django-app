from django import forms
from .models import Book, Quote, Theme


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = '__all__'
        exclude = ('book',)
        can_delete = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    book = forms.ModelChoiceField(
        queryset=Book.objects.all(),
        widget=forms.HiddenInput(),
        empty_label='-----'
    )


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        exclude = ('read_at', 'comment', 'updated_at',)
        can_delete = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ThemeCommentForm(forms.ModelForm):
    class Meta:
        model = Theme
        fields = ('comment',)


class ThemeForm(forms.ModelForm):
    class Meta:
        model = Theme
        fields = '__all__'
