from django import forms
from django.core.validators import MinValueValidator

class CartItemForm(forms.Form):
    quantity = forms.IntegerField(
        validators=[MinValueValidator(1, message="Quantity must be at least 1.")],
        error_messages={
            'required': 'This field is required.',
        }
    )