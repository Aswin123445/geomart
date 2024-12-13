
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django import forms
from .models import UserData
from django.core.validators import RegexValidator
class SignUpForm(UserCreationForm):
    name = forms.CharField(required=True, min_length=3, max_length=40)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(
        required=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid phone number.")],
    )
    def clean_email(self):
        email = self.cleaned_data.get('email')
        print(email)
        user=UserData.objects.filter(email=email).first()
        if user:
            if user.is_email_verified :
               raise forms.ValidationError("A user with this email already exists.")
            else :
               print('need to verify')
        return email

    # def clean_phone_number(self):
    #     phone_number = self.cleaned_data.get('phone_number')
    #     if not phone_number.startswith('+91'):
    #         phone_number = '+91' + phone_number
        
    #     if UserData.objects.filter(phone_number=phone_number).exists():
    #         raise forms.ValidationError("A user with this phone number already exists.")
    #     return phone_number
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Ensure phone number starts with +91
        if not phone_number.startswith('+91'):
            phone_number = f'+91 + {phone_number}'

        # Query the UserData model for the phone number
        user = UserData.objects.filter(phone_number=phone_number).first()

        if user:
            if user.is_phone_number_verified:
                raise forms.ValidationError("A user with this phone number already exists and is verified.")
            else:
                self.cleaned_data['otp_verification'] = phone_number
                print("done")

        return phone_number


    def save(self, commit=True):
        print('within save method')
        user = super().save(commit=False)
        print(self.cleaned_data)
        print(f'{user} user activated')
        user.name = self.cleaned_data['name']
        user.phone_number = self.cleaned_data['phone_number']
        print(self.cleaned_data['name'])
        print(self.cleaned_data['email'])
        user.email = self.cleaned_data['email']
        user.is_active = False
        if commit:
            user.save()
        return user

    class Meta:
        model = UserData
        fields = [ 'name', 'password1', 'password2']
        
        
#forgot passord form
class ForgotPassword(forms.Form):
    print("helo")
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
    


#there are many errors to fix in this area
class SignInForm(forms.Form):
    email_or_phone = forms.CharField(
        max_length=254,
        required=True,
    )
    password = forms.CharField(widget=forms.PasswordInput)
    phone_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid phone number.")
    def clean(self):
        cleaned_data = super().clean()
        email_or_phone = cleaned_data.get('email_or_phone')
        password = cleaned_data.get('password')
        if not email_or_phone or not password :
            raise forms.ValidationError("both the forms are requeired")

        if '@'  in email_or_phone :
            user = authenticate(email=email_or_phone, password=password)
            print(user)
        else :
            try :
                email_or_phone='+91'+email_or_phone
                self.phone_validator(email_or_phone) 
                user = UserData.objects.get(phone_number=email_or_phone) 
                if user is not None :  
                    cleaned_data['email_or_phone']=user.email
                    user = authenticate(email=user.email,password=password)
            except forms.ValidationError:
                raise forms.ValidationError("The phone number you entered is invalid.")
            except UserData.DoesNotExist :
                raise forms.ValidationError("Phone number not found.")

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
