from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from uuid import uuid4

# OAuth Providers: Google, Facebook, Apple (Iphone users)

class User(AbstractUser):
    '''Purpose: For Authentication only'''
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    # Make email login instead of username
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # or remove username entirely later

    def __str__(self):
        return self.email
    

class UserPreference(models.Model):
    '''Purpose: For User Preferences only'''
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="preferences"
    )

    categories = models.ManyToManyField
    receive_emails = models.BooleanField(default=True)
    dark_mode = models.BooleanField(default=False)
    

class Address(models.Model):
    '''Purpose: For User Addresses only'''
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    address_line = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    is_default = models.BooleanField(default=False)


class UserAuthProvider(models.Model):
    PROVIDER_CHOICES = (
        ("google", "Google"),
        ("facebook", "Facebook"),
        ("apple", "Apple"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="auth_providers"
    )

    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_user_id = models.CharField(max_length=255)

    class Meta:
        unique_together = ("provider", "provider_user_id")