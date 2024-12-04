
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django import forms
from .models import UserData
from django.core.validators import RegexValidator
class SignUpForm(UserCreationForm):
    name = forms.CharField(required=True, min_length=3, max_length=40)
    phone_number = forms.CharField(
        required=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid phone number.")],
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserData.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if UserData.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.name = self.cleaned_data['name']
        user.phone_number = self.cleaned_data['phone_number']
        if commit:
            user.save()
        return user

    class Meta:
        model = UserData
        fields = ['email', 'name', 'phone_number', 'password1', 'password2']

class SignInForm(forms.Form):
    email = forms.EmailField(max_length=254, required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if user is None:
            raise forms.ValidationError("Invalid login credentials.")
        if not user.is_active:
            raise forms.ValidationError("This account is inactive.")
        return cleaned_data
