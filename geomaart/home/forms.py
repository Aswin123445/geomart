from django import forms

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

    def clean_address_type(self):
        address_type = self.cleaned_data.get('address_type')
        print(address_type)
        try:
            address_type = int(address_type)
            if address_type not in [1, 2, 3]:
                raise forms.ValidationError('Invalid address type selection.')
        except ValueError:
            raise forms.ValidationError('Address type must be an integer.')
        return address_type

    def clean(self):
        cleaned_data = super().clean()
        street_address = cleaned_data.get('street_address')
        city = cleaned_data.get('city')

        if street_address and len(street_address.split()) < 2:
            self.add_error('street_address', 'Street address must contain at least two words.')

        if city and city.isdigit():
            self.add_error('city', 'City name cannot contain only numbers.')

        return cleaned_data
