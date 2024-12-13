from django import forms
from accounts.models import UserData
import re
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

class UserDataUpdation(forms.Form):
    name = forms.CharField(
        max_length=150,
        label="Username"
    )
    email = forms.EmailField(
        label="Email"
    )
    phone_number = forms.CharField(
        required=True,

    )
    role = forms.CharField(
        label="Role"
    )
    status = forms.CharField(
        label="Status"
    )
    
    def __init__(self, *args, **kwargs):
        self.current_user_id = kwargs.pop('current_user_id', None)  # Accept current user ID
        super().__init__(*args, **kwargs)

    def clean_status(self):
        avail_status = ['active', 'inactive']
        status = self.cleaned_data.get('status')  # Get the status value from cleaned data
        if status not in avail_status:
            raise forms.ValidationError("Invalid status. Choose either 'active' or 'inactive'.")
        
        # Add 'is_active' to cleaned_data based on status
        self.cleaned_data['is_active'] = (status == 'active')
        return status  # Return the cleaned status value

    def clean_role(self):
        avail_roles = ['ADMIN', 'DELIVERY_PARTNER', 'USER']
        role = self.cleaned_data.get('role')  # Get the role value from cleaned data
        if role not in avail_roles:
            raise forms.ValidationError("Invalid role. Choose a valid role.")
        
        # Add custom keys based on the role
        if role == 'ADMIN':
            self.cleaned_data['is_staff'] = True
        elif role == 'DELIVERY_PARTNER':
            self.cleaned_data['is_delivery_boy'] = True
        return role  # Return the cleaned role value

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Exclude the current user's record while checking for duplicates
        print(self.current_user_id)
        query=UserData.objects.filter(email=email).exclude(id=self.current_user_id).exists()
        if query:
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        regex = r"^\+91\d{10}$"
        # Ensure the phone number starts with +91
        if  not phone_number.startswith('+91') :
            if not phone_number.startswith('None'):
              phone_number = f'+91{phone_number}'
        if not re.match(regex, phone_number):
            if phone_number != 'None':
             raise ValidationError("Enter a valid phone number in the format +91XXXXXXXXXX.")
        
        # Exclude the current user's record while checking for duplicates
        if UserData.objects.filter(phone_number=phone_number).exclude(id=self.current_user_id).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        
        return phone_number
    
class AdminUserAddForm(forms.Form):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('user', 'User'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}),
        label="Password",
        required=True,
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}),
        label="Confirm Password",
        required=True,
    )
    name = forms.CharField(
        max_length=100,
        required=True,
        label="Name",
    )
    email = forms.EmailField(
        required=True,
        label="Email",
    )
    phone = forms.CharField(
        required=True,
        label="Phone Number",
        error_messages={'invalid': 'Enter a valid phone number (10-15 digits).'},
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        label="Role",
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=True,
        label="Status",
    )
    def clean_password1(self):
        print('helo')
        password = self.cleaned_data.get('password1')
        try:
            # Use Django's built-in password validators
            validate_password(password)
        except ValidationError as e:
            raise ValidationError(e.messages)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password1')
        confirm_password = cleaned_data.get('password2')

        # Check if passwords match
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")

        return cleaned_data
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise forms.ValidationError("Name must be at least 3 characters long.")
        return name

    def clean_phone(self):
        regex = r"^\+91\d{10}$"
        phone = self.cleaned_data.get('phone')
        if  not phone.startswith('+91') :
              phone = f'+91{phone}'
        if not re.match(regex, phone):
            raise ValidationError("Enter a valid phone number in the format +91XXXXXXXXXX.")
        return phone
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Regex pattern to validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValidationError("Enter a valid email address.")

        # Check for duplicate emails in the database
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered. Please use a different email address.")
        
        return email
    

    

