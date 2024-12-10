from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
from allauth.account.signals import user_logged_in

class UserManager(BaseUserManager):
    def create_user(self, email, name, phone_number=None, password=None, is_active=True, is_staff=False, is_superuser=False, is_delivery_boy=False):
        """Creates and returns a user with the given details."""
        if not email:
            raise ValueError("The email field must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            phone_number=phone_number,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_delivery_boy=is_delivery_boy,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone_number=None, password=None):
        """Create and return a superuser."""
        return self.create_user(
            email=email,
            name=name,
            phone_number=phone_number,
            password=password,
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )

    def create_delivery_boy(self, email, name, phone_number=None, password=None):
        """Create and return a delivery boy."""
        return self.create_user(
            email=email,
            name=name,
            phone_number=phone_number,
            password=password,
            is_active=True,
            is_delivery_boy=True,
        )

class UserData(AbstractBaseUser, PermissionsMixin):
    """Custom User model."""
    email = models.EmailField(
        max_length=255,
        unique=True,
        null=False,
        verbose_name="User's email address",
        help_text="Enter a valid email address"
    )
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")]
    )
    name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)  # Implies admin privileges
    is_delivery_boy = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_phone_number_verified = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone_number']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    social_links = models.JSONField(null=True, blank=True)  # Example: {"twitter": "link", "linkedin": "link"}

    def __str__(self):
        return f"Profile of {self.user.name}"

class Address(models.Model):
    ADDRESS_TYPES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPES, default='home')
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    is_primary = models.BooleanField(default=False)  


    def __str__(self):
        return f"{self.address_type.capitalize()} Address of {self.user.name}"


