
from django import forms
import re

class AddressForm(forms.Form):
    ADDRESS_TYPE_CHOICES = [
        ('1', 'Home'),
        ('2', 'Work'),
        ('3', 'Other'),
    ]

    addressType = forms.ChoiceField(
        choices=ADDRESS_TYPE_CHOICES,
        required=True,
        label="Address Type",
        error_messages={
            'required': 'Please select an address type.',
            'invalid_choice': 'Invalid address type selection.',
        }
    )
    streetAddress = forms.CharField(
        max_length=255,
        required=True,
        label="Street Address",
        widget=forms.TextInput(attrs={'placeholder': '123 Main St'}),
        error_messages={
            'required': 'Street address is required.',
            'max_length': 'Street address cannot exceed 255 characters.',
        }
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        label="City",
        widget=forms.TextInput(attrs={'placeholder': 'City'}),
        error_messages={
            'required': 'City is required.',
            'max_length': 'City cannot exceed 100 characters.',
        }
    )
    state = forms.CharField(
        max_length=100,
        required=True,
        label="State",
        widget=forms.TextInput(attrs={'placeholder': 'State'}),
        error_messages={
            'required': 'State is required.',
            'max_length': 'State cannot exceed 100 characters.',
        }
    )
    postalCode = forms.RegexField(
        regex=r'^\d{5,6}$',
        required=True,
        label="Postal Code",
        widget=forms.TextInput(attrs={'placeholder': '123456'}),
        error_messages={
            'required': 'Postal code is required.',
            'invalid': 'Please enter a valid postal code (5 or 6 digits).',
        }
    )
    country = forms.CharField(
        max_length=100,
        required=True,
        label="Country",
        widget=forms.TextInput(attrs={'placeholder': 'Country'}),
        error_messages={
            'required': 'Country is required.',
            'max_length': 'Country cannot exceed 100 characters.',
        }
    )
    primaryAddress = forms.BooleanField(
        required=False,
        label="Set as Primary Address",
    )

    def clean_city(self):
        """
        Validate the city field to ensure it does not contain special characters.
        """
        city = self.cleaned_data.get('city')
        if not re.match(r'^[a-zA-Z\s-]+$', city):  # Only allow letters, spaces, and hyphens
            raise forms.ValidationError('City name can only contain letters, spaces, or hyphens.')
        return city

    def clean_state(self):
        """
        Validate the state field to ensure it does not contain special characters.
        """
        state = self.cleaned_data.get('state')
        if not re.match(r'^[a-zA-Z\s-]+$', state):  # Only allow letters, spaces, and hyphens
            raise forms.ValidationError('State name can only contain letters, spaces, or hyphens.')
        return state

    def clean_streetAddress(self):
        """
        Validate the street address field to ensure valid characters are allowed.
        """
        street_address = self.cleaned_data.get('streetAddress')
        if not re.match(r'^[\w\s\.,-]+$', street_address):  # Allow alphanumeric, spaces, dots, commas, hyphens
            raise forms.ValidationError('Street address contains invalid characters.')
        return street_address

    def clean_country(self):
        """
        Validate the country field to ensure it does not contain special characters.
        """
        country = self.cleaned_data.get('country')
        if not re.match(r'^[a-zA-Z\s-]+$', country):  # Only allow letters, spaces, and hyphens
            raise forms.ValidationError('Country name can only contain letters, spaces, or hyphens.')
        return country

    def clean(self):
        """
        Perform any additional cross-field validation here.
        """
        cleaned_data = super().clean()
        return cleaned_data

class ReviewForm(forms.Form):
    review_text = forms.CharField(
        max_length=1000,
        required=True,
    )
    rating = forms.IntegerField(
        required=True,
    )
    id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=True
    )
    def clean_review_text(self):
        """Ensure the review text is not empty."""
        review_text = self.cleaned_data.get('review_text', '').strip()
        if not review_text:
            raise forms.ValidationError("Review text cannot be empty.")
        return review_text

    def clean_rating(self):
        """Convert the rating to an integer."""
        rating = self.cleaned_data.get('rating')
        try:
            return int(rating)
        except ValueError:
            raise forms.ValidationError("Invalid rating value.")

