from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class PaymentType(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100)
    code = models.PositiveIntegerField(unique=True)  # sehir_id

    def __str__(self):
        return self.name

class District(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city.name} - {self.name}"
    
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
    company = models.ForeignKey('company.Company', on_delete=models.SET_NULL, null=True, blank=True)
    last_name = models.CharField(max_length=150,  blank=True, null=True)
    full_name = models.CharField(max_length=150,  blank=True, null=True)
    phone = models.CharField(max_length=60, unique=True, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
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
    user_active = models.BooleanField(default=False, verbose_name='User Active')
    sms_code = models.CharField(max_length=6, blank=True, null=True)
    sms_code_created = models.DateTimeField(blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False, verbose_name='Phone Verified')
    is_email_verified = models.BooleanField(default=False, verbose_name='Email Verified')
    payment_type = models.ForeignKey(PaymentType, on_delete=models.SET_NULL, null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'