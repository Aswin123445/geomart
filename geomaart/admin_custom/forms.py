from django import forms
from accounts.models import UserData
import re
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .validationslogic import coupon_special_character_check
from admin_custom.models import Category
from .validationslogic import category_id_valid_check,category_description_empty_check,category_name_validations_check
from .validationslogic import location_name_validations_check,product_integer_value_negative_check
from .validationslogic import location_valid_check,category_valid_check
from .models import Offer
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

# class categoryValidation(forms.Form) :
#     categoryName = forms.CharField(
#         required=True,
#         min_length=3,
#         strip=True,
#         error_messages={
#             'min_length':'minium 5 characteres is requerid'
#         },
#         validators=[category_name_validations_check]
#     )
#     categoryId = forms.IntegerField(min_value=0,validators=[category_id_valid_check],required= False)
#     categoryDescription = forms.CharField(
#         required=True,
#         min_length=5,
#         max_length=400,
#         validators=[category_description_empty_check]
#     )
#     categoryStatus=forms.IntegerField(min_value=1,max_value=3)



class categoryValidation(forms.Form):
    categoryName = forms.CharField(
        required=True,
        min_length=5,
        max_length=50,
        strip=True,
        label="Category Name",
        error_messages={
            'required': 'Category name is required.',
            'min_length': 'Minimum 5 characters are required for the category name.',
            'max_length': 'Category name cannot exceed 50 characters.',
        },
        validators=[category_name_validations_check]
    )
    categoryId = forms.IntegerField(
        min_value=0,
        required=False,
        label="Category ID",
        error_messages={
            'min_value': 'Category ID must be a positive integer.',
        },
        validators=[category_id_valid_check]
    )
    categoryDescription = forms.CharField(
        required=True,
        min_length=5,
        max_length=400,
        label="Category Description",
        widget=forms.Textarea(attrs={'placeholder': 'Enter a detailed category description'}),
        error_messages={
            'required': 'Category description is required.',
            'min_length': 'Category description must be at least 5 characters long.',
            'max_length': 'Category description cannot exceed 400 characters.',
        },
        validators=[category_description_empty_check]
    )
    categoryStatus = forms.IntegerField(
        min_value=1,
        max_value=3,
        required=True,
        label="Category Status",
        error_messages={
            'required': 'Category status is required.',
            'min_value': 'Invalid category status. It must be between 1 and 3.',
            'max_value': 'Invalid category status. It must be between 1 and 3.',
        }
    )

    def clean_categoryName(self):
        category_name = self.cleaned_data.get('categoryName')
        if category_name.isdigit():
            raise ValidationError("Category name cannot be entirely numeric.")
        return category_name

    def clean_categoryStatus(self):
        status = self.cleaned_data.get('categoryStatus')
        valid_statuses = [1, 2, 3]  # Define valid statuses
        if status not in valid_statuses:
            raise ValidationError("Invalid category status selected.")
        return status
    def clean_categoryName(self):
        category_name = self.cleaned_data.get('categoryName')
        # Check for case-insensitive duplicates
        if Category.objects.filter(name__iexact=category_name).exists():
            raise ValidationError(f"The category '{category_name}' already exists.")
        return category_name
    def clean(self):
        cleaned_data = super().clean()
        category_name = cleaned_data.get('categoryName')
        category_description = cleaned_data.get('categoryDescription')

        # Cross-field validation
        if category_name and category_description:
            if category_name.lower() in category_description.lower():
                self.add_error(
                    'categoryDescription',
                    'Category description should not contain the category name.'
                )
        
        return cleaned_data

    
from django import forms
from django.core.exceptions import ValidationError
from .models import Location, Product  # Assuming there's a Location model
import re

class LocationValidation(forms.Form):
    district = forms.CharField(
        max_length=100,
        min_length=3,
        strip=True,
        required=True,
        validators=[location_name_validations_check],  # Custom validator
        error_messages={
            'required': 'District name is required.',
            'min_length': 'The district name is too short, please increase the length.',
            'max_length': 'The district name exceeds the maximum limit of 100 characters.',
        },
    )
    description = forms.CharField(
        max_length=500,
        min_length=3,
        required=True,
        validators=[location_name_validations_check],  # Custom validator
        error_messages={
            'required': 'Description is required.',
            'min_length': 'The description is too short, please increase the length.',
            'max_length': 'The description exceeds the maximum limit of 500 characters.',
        },
    )

    def clean_district(self):
        """
        Ensure district name is unique, case-insensitive, and doesn't contain special characters or numbers.
        """
        district = self.cleaned_data['district'].strip().lower()

        # Check for special characters and numbers
        if re.search(r'[^a-z\s]', district):  # Allows only letters and spaces
            raise ValidationError('District name should contain only letters and spaces.')

        # Check for case-insensitive uniqueness
        if Location.objects.filter(district__iexact=district).exists():
            raise ValidationError(f"A district with the name '{district}' already exists.")

        return district

    def clean_description(self):
        """
        Validate that the description is meaningful and doesn't contain invalid characters.
        """
        description = self.cleaned_data['description'].strip()

        # Ensure description has at least two words
        if len(description.split()) < 2:
            raise ValidationError('Description must contain at least two words.')

        # Check for invalid characters
        if re.search(r'[^\w\s.,]', description):  # Allows letters, numbers, spaces, commas, and periods
            raise ValidationError('Description contains invalid characters.')

        return description

    def clean(self):
        """
        Additional checks on the entire form.
        """
        cleaned_data = super().clean()

        # Check if district and description are the same (optional, depends on use case)
        district = cleaned_data.get('district')
        description = cleaned_data.get('description')

        if district and description and district.lower() in description.lower():
            self.add_error(
                'description', 'Description should not merely repeat the district name.'
            )

        return cleaned_data


class ProductValidation(forms.Form):
    name = forms.CharField(
        min_length=3,
        max_length=40,
        required=True,
        strip=True,
        validators=[category_name_validations_check],  # Custom validator
        error_messages={
            'required': 'This field is required.',
            'min_length': 'Product name should be at least 3 characters.',
            'max_length': 'Product name cannot exceed 40 characters.'
        }
    )
    description = forms.CharField(
        min_length=3,
        max_length=2000,
        required=True,
        validators=[category_name_validations_check],  # Custom validator
        error_messages={
            'required': 'This field is required.',
            'min_length': 'Description should be at least 3 characters.',
            'max_length': 'Description cannot exceed 2000 characters.'
        }
    )
    price = forms.IntegerField(
        min_value=5,
        required=True,
        validators=[product_integer_value_negative_check],  # Custom validator
        error_messages={
            'required': 'This field is required.',
            'min_value': 'Price must be 5 or more.'
        }
    )
    stock = forms.IntegerField(
        min_value=1,
        required=True,
        validators=[product_integer_value_negative_check],  # Custom validator
        error_messages={
            'required': 'This field is required.',
            'min_value': 'Stock must be more than 0.'
        }
    )
    location = forms.IntegerField(
        min_value=0,
        required=True,
        validators=[location_valid_check],  # Custom validator
        error_messages={
            'invalid': 'Please select a valid location.'
        }
    )
    category = forms.IntegerField(
        min_value=0,
        required=True,
        validators=[category_valid_check],  # Custom validator
        error_messages={
            'invalid': 'Please select a valid category.'
        }
    )
    culturalbackground = forms.CharField(
        required=True,
        min_length=20,
        strip=True,
        error_messages={
            'required': 'This field is required.',
            'min_length': 'Cultural background should be at least 20 characters.'
        }
    )

    def clean_name(self):
        """
        Check if a product with the same name already exists (case-insensitive).
        """
        name = self.cleaned_data['name'].strip().upper()

        # Check for case-insensitive uniqueness
        if Product.objects.filter(name__iexact=name).exists():
            raise ValidationError(f"A product with the name '{name}' already exists.")

        return name

    def clean(self):
        """
        Perform additional validation checks across the form fields.
        """
        cleaned_data = super().clean()

        # You can add additional cross-field validation if needed
        # For example, you can check if price and stock make sense logically

        price = cleaned_data.get('price')
        stock = cleaned_data.get('stock')

        if price and stock and stock > 1000 and price < 5:
            self.add_error('price', 'For high stock, the price should be at least 5.')

        return cleaned_data

class ProductUpdateForm(forms.Form):
    name = forms.CharField(
        min_length=3,
        max_length=40,
        required=False,  # Allow the name to remain unchanged
        strip=True,
        validators=[category_name_validations_check],  # Custom validator
        error_messages={
            'min_length': 'Product name should be at least 3 characters.',
            'max_length': 'Product name cannot exceed 40 characters.'
        }
    )
    description = forms.CharField(
        min_length=3,
        max_length=2000,
        required=False,  # Allow the description to remain unchanged
        validators=[category_name_validations_check],  # Custom validator
        error_messages={
            'min_length': 'Description should be at least 3 characters.',
            'max_length': 'Description cannot exceed 2000 characters.'
        }
    )
    price = forms.IntegerField(
        min_value=5,
        required=False,  # Allow the price to remain unchanged
        validators=[product_integer_value_negative_check],  # Custom validator
        error_messages={
            'min_value': 'Price must be 5 or more.'
        }
    )
    stock = forms.IntegerField(
        min_value=1,
        required=False,  # Allow the stock to remain unchanged
        validators=[product_integer_value_negative_check],  # Custom validator
        error_messages={
            'min_value': 'Stock must be more than 0.'
        }
    )
    location = forms.IntegerField(
        min_value=0,
        required=False,  # Allow the location to remain unchanged
        validators=[location_valid_check],  # Custom validator
        error_messages={
            'invalid': 'Please select a valid location.'
        }
    )
    category = forms.IntegerField(
        min_value=0,
        required=False,  # Allow the category to remain unchanged
        validators=[category_valid_check],  # Custom validator
        error_messages={
            'invalid': 'Please select a valid category.'
        }
    )
    culturalbackground = forms.CharField(
        required=False,  # Allow the cultural background to remain unchanged
        min_length=20,
        strip=True,
        error_messages={
            'min_length': 'Cultural background should be at least 20 characters.'
        }
    )

    # def clean_name(self):
    #     """
    #     Check if a product with the same name (other than the current product) already exists (case-insensitive).
    #     """
    #     # Only check if name is provided for update
    #     name = self.cleaned_data.get('name')
    #     if name:
    #         name = name.strip().upper()
    #         # Assuming `product_id` is passed as a part of the form data
    #         product_id = self.initial.get('product_id')
    #         if Product.objects.filter(name__iexact=name).exclude(id=product_id).exists():
    #             raise ValidationError(f"A product with the name '{name}' already exists.")
    #     return name

    def clean(self):
        """
        Perform additional validation checks across the form fields.
        """
        cleaned_data = super().clean()

        price = cleaned_data.get('price')
        stock = cleaned_data.get('stock')

        if price and stock and stock > 1000 and price < 5:
            self.add_error('price', 'For high stock, the price should be at least 5.')

        return cleaned_data

from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Coupon  # Replace with the actual model name

class CouponCreationForm(forms.Form):
    coupon_code = forms.CharField(
        max_length=6,
        min_length=6,
        validators=[coupon_special_character_check]
    )
    coupon_type = forms.IntegerField(
        min_value=1,
        max_value=3
    )
    start_date = forms.DateField()
    enddate = forms.DateField()
    coupon_limit = forms.IntegerField(
        min_value=1,
    )
    discount_value = forms.IntegerField(min_value=1)
    limit_per_user = forms.IntegerField(
        min_value=1
    )
    min_purchase_amount = forms.IntegerField()
    status = forms.IntegerField(min_value=0, max_value=1)
    
    def clean_coupon_code(self):
        """Ensure the coupon code is unique and converted to uppercase."""
        data = self.cleaned_data['coupon_code']
        if data:
            data = data.upper()  # Convert to uppercase
            # Check uniqueness against the database
            if Coupon.objects.filter(code=data).exists():
                raise ValidationError("A coupon with this code already exists.")
        else:
            raise ValidationError("This field cannot be empty.")
        return data

    def clean(self):
        """Ensure start date is less than end date."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        enddate = cleaned_data.get('enddate')
        
        # Check that start_date is less than enddate
        if start_date and enddate:
            if start_date >= enddate:
                raise ValidationError(
                    "Start date must be earlier than the end date."
                )
        
        # Optional: Check start date is not in the past
        if start_date and start_date < date.today():
            raise ValidationError("Start date cannot be in the past.")
        return cleaned_data
class CouponUpdateForm(forms.Form):
    coupon_code = forms.CharField(
        max_length=6,
        min_length=6,
        validators=[coupon_special_character_check]
    )
    coupon_type = forms.IntegerField(
        min_value=1,
        max_value=3
    )
    start_date = forms.DateField()
    enddate = forms.DateField()
    coupon_limit = forms.IntegerField(
        min_value=1,
    )
    discount_value = forms.IntegerField(min_value=1)
    limit_per_user = forms.IntegerField(
        min_value=1
    )
    min_purchase_amount = forms.IntegerField()
    status = forms.IntegerField(min_value=0, max_value=1)
    
    def clean_coupon_code(self):
        """Ensure the coupon code is unique and converted to uppercase."""
        data = self.cleaned_data['coupon_code']
        if data:
            data = data.upper()  # Convert to uppercase
        else:
            raise ValidationError("This field cannot be empty.")
        return data

    def clean(self):
        """Ensure start date is less than end date."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        enddate = cleaned_data.get('enddate')
        
        # Check that start_date is less than enddate
        if start_date and enddate:
            if start_date >= enddate:
                raise ValidationError(
                    "Start date must be earlier than the end date."
                )
        


class CouponFilterForm(forms.Form):
    status = forms.NullBooleanField()
    type = forms.IntegerField()
    def clean_type(self):
        data = self.cleaned_data['type']
        if data == 0 :
            data = None
        return data
from django import forms
from django.core.exceptions import ValidationError

from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import now

class DateValidations(forms.Form):
    start_date = forms.DateField(required=False)
    enddate = forms.DateField(required=False)

    def clean(self):
        """
        Custom clean method to validate start_date and enddate.
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        enddate = cleaned_data.get('enddate')
        today = now().date()  # Get today's date

        # Check if only one of the dates is provided
        if (start_date and not enddate) or (enddate and not start_date):
            raise ValidationError("Both start date and end date must be provided if either is entered.")

        # Check if start_date is later than enddate
        if start_date and enddate and start_date > enddate:
            raise ValidationError("Start date cannot be later than end date.")

        # Check if enddate is in the future
        if enddate and enddate > today:
            raise ValidationError("End date cannot be in the future.")

        return cleaned_data

class OfferForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    offer_type = forms.ChoiceField(choices=[('1', 'Percentage'), ('2', 'Fixed Amount')], required=True)
    discount_value = forms.DecimalField(min_value=0, required=True)
    start_date = forms.DateField(required=True)
    end_date = forms.DateField(required=True)
    is_active = forms.BooleanField(required=False)

    def clean_name(self):
        # Capitalize the name field value
        name = self.cleaned_data['name'].capitalize()
        
        # Check for duplicate names in the database
        if Offer.objects.filter(name=name).exists():
            raise forms.ValidationError("This offer name already exists.")
        
        return name

    def clean_start_date(self):
        start_date = self.cleaned_data['start_date']
        today = date.today()

        if start_date < today:
            raise forms.ValidationError("Start date cannot be in the past.")
        return start_date

    def clean_end_date(self):
        end_date = self.cleaned_data['end_date']
        today = date.today()

        if end_date < today:
            raise forms.ValidationError("End date cannot be in the past.")
        return end_date

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Validate that start_date is earlier than or equal to end_date
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date must be earlier than or equal to the end date.")
        return cleaned_data

class OfferEdit(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    offer_type = forms.ChoiceField(choices=[('1', 'Percentage'), ('2', 'Fixed Amount')], required=True)
    discount_value = forms.DecimalField(min_value=0, required=True)
    start_date = forms.DateField(required=True)
    end_date = forms.DateField(required=True)
    is_active = forms.BooleanField(required=False)

    def clean_name(self):
        # Capitalize the name field value
        name = self.cleaned_data['name'].capitalize()
        return name

    def clean_start_date(self):
        start_date = self.cleaned_data['start_date']
        today = date.today()

        if start_date < today:
            raise forms.ValidationError("Start date cannot be in the past.")
        return start_date

    def clean_end_date(self):
        end_date = self.cleaned_data['end_date']
        today = date.today()

        if end_date < today:
            raise forms.ValidationError("End date cannot be in the past.")
        return end_date

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Validate that start_date is earlier than or equal to end_date
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date must be earlier than or equal to the end date.")
        return cleaned_data


    
        
  
        
