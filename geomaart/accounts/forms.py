
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django import forms
from .models import UserData
from django.core.validators import RegexValidator


class SignUpForm(UserCreationForm):
    name = forms.CharField(
        required=True,
        min_length=3,
        max_length=40,
        label="Full Name",
        error_messages={
            "required": "Name is required.",
            "min_length": "Name must be at least 3 characters long.",
            "max_length": "Name cannot exceed 40 characters.",
        },
    )
    email = forms.EmailField(
        required=True,
        label="Email Address",
        error_messages={
            "required": "Email is required.",
            "invalid": "Enter a valid email address.",
        },
    )
    phone_number = forms.CharField(
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Enter a valid phone number (e.g., +911234567890)."
            )
        ],
        label="Phone Number",
        error_messages={"required": "Phone number is required."},
    )

    def clean_email(self):
        """
        Validate email to ensure it is unique and properly formatted.
        """
        email = self.cleaned_data.get('email')
        user = UserData.objects.filter(email=email).first()
        if user:
            if user.is_email_verified:
                raise forms.ValidationError("A user with this email already exists.")
            else:
                # Handle unverified emails
                self.cleaned_data['resend_verification_email'] = email
        return email

    def clean_phone_number(self):
        """
        Validate phone number for proper format and uniqueness.
        """
        phone_number = self.cleaned_data.get('phone_number')

        # Ensure phone number starts with +91
        if not phone_number.startswith('+91'):
            phone_number = f'+91{phone_number}'

        # Query the UserData model for the phone number
        user = UserData.objects.filter(phone_number=phone_number).first()
        if user:
            if user.is_phone_number_verified:
                raise forms.ValidationError("A user with this phone number already exists and is verified.")
            else:
                # Handle unverified phone numbers
                self.cleaned_data['otp_verification'] = phone_number
        return phone_number

    def clean_name(self):
        """
        Validate name for prohibited characters and length.
        """
        name = self.cleaned_data.get('name')
        if not name.replace(' ', '').isalpha():
            raise forms.ValidationError("Name must only contain letters and spaces.")
        return name

    def save(self, commit=True):
        """
        Override the save method to handle additional fields and user activation.
        """
        user = super().save(commit=False)
        user.name = self.cleaned_data['name']
        user.phone_number = self.cleaned_data['phone_number']
        user.email = self.cleaned_data['email']
        user.is_active = False  # User must verify email/phone before activation

        if commit:
            user.save()

        return user

    class Meta:
        model = UserData
        fields = ['name', 'email', 'phone_number', 'password1', 'password2']

        
#forgot passord form
class ForgotPassword(forms.Form):
    phone_number = forms.CharField(
       required=True,
       validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid phone number.")],
    )
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        phone_number = ''.join(phone_number.split())
        # Ensure phone number starts with +91
        if not phone_number.startswith('+91'):
            phone_number = '+91' + phone_number
        return phone_number
    


class SignInForm(forms.Form):
    email_or_phone = forms.CharField(
        max_length=254,
        required=True,
        label="Email or Phone",
        help_text="Enter your registered email or phone number.",
        error_messages={
            "required": "Email or phone number is required.",
            "max_length": "Input cannot exceed 254 characters.",
        },
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Password",
        error_messages={
            "required": "Password is required.",
        },
    )

    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Enter a valid phone number (e.g., +911234567890)."
    )

    COUNTRY_CODE = "+91"  # Default country code

    def clean_email_or_phone(self):
        """
        Validate email_or_phone to ensure it's a valid email or phone format.
        """
        email_or_phone = self.cleaned_data.get('email_or_phone')

        # Validate the length of the input
        if len(email_or_phone) > 254:
            raise forms.ValidationError("Input length exceeds the maximum allowed limit.")

        # Check for invalid characters
        if not email_or_phone.replace('@', '').replace('.', '').replace('+', '').isalnum():
            raise forms.ValidationError("Invalid characters in email or phone number.")

        return email_or_phone

    def clean(self):
        """
        Clean and validate the form data to handle all edge cases.
        """
        cleaned_data = super().clean()
        email_or_phone = cleaned_data.get('email_or_phone')
        password = cleaned_data.get('password')

        # Check if both fields are provided
        if not email_or_phone or not password:
            raise forms.ValidationError("Both email/phone and password are required.")

        user = None

        # Email-based authentication
        if '@' in email_or_phone:
            # Validate email format
            if '.' not in email_or_phone or email_or_phone.count('@') != 1:
                raise forms.ValidationError("Enter a valid email address.")
            user = authenticate(email=email_or_phone, password=password)
        
        # Phone-based authentication
        else:
            try:
                formatted_phone = self.COUNTRY_CODE + email_or_phone
                self.phone_validator(formatted_phone)

                try:
                    # Check if the phone number exists
                    user_data = UserData.objects.get(phone_number=formatted_phone)

                    # Ensure the user has an email linked
                    if not user_data.email:
                        raise forms.ValidationError("No email is linked to this phone number.")

                    # Update cleaned data with email
                    cleaned_data['email_or_phone'] = user_data.email
                    user = authenticate(email=user_data.email, password=password)

                except UserData.DoesNotExist:
                    raise forms.ValidationError("Phone number not found.")
            
            except forms.ValidationError as e:
                raise forms.ValidationError(f"Phone number validation error: {e}")

        # Validate authentication result
        if user is None:
            raise forms.ValidationError("Invalid login credentials.")
        if not user.is_active:
            raise forms.ValidationError("This account is inactive.")

        return cleaned_data

    
class FogotPasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        try:
            validate_password(password1)  # Apply Django's password validation
        except forms.ValidationError as e:
            raise forms.ValidationError(e.messages)  # Pass validation errors to the form
        return password1
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match. Please try again.")
        return cleaned_data
