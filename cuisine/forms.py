from django import forms
from .models import Dish, Food, Recipe, DishType


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = '__all__'
        exclude = ('cooked_count', 'foods', 'condiments', 'last_created_at')
        can_delete = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    RecipeFormset = forms.inlineformset_factory(
        Dish, Recipe, fields='__all__',
        extra=8, can_delete=False
    )
