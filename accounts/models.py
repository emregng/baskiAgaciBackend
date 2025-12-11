from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class Sector(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.name

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email')
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=150,  blank=True, null=True)
    last_name = models.CharField(max_length=150,  blank=True, null=True)
    full_name = models.CharField(max_length=150,  blank=True, null=True)
    phone = models.CharField(max_length=60, unique=True, blank=True, null=True)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='Groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        verbose_name='User Permissions'
    )
    is_active = models.BooleanField(default=True, verbose_name='Active Status')
    sms_code = models.CharField(max_length=6, blank=True, null=True)
    sms_code_created = models.DateTimeField(blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False, verbose_name='Phone Verified')
    is_email_verified = models.BooleanField(default=False, verbose_name='Email Verified')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'