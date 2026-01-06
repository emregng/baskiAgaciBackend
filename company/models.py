from django.db import models
from media.models import Media

# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    sector = models.ForeignKey('accounts.Sector', on_delete=models.SET_NULL, related_name='companies',null=True,blank=True)
    taxOffice = models.CharField(max_length=255, blank=True, null=True)
    taxNumber = models.CharField(max_length=50, blank=True, null=True)
    social_media = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class CompanyMedia(models.Model):
    STATUS_PENDING = 1
    STATUS_APPROVED = 0
    STATUS_REJECTED = 2

    STATUS_CHOICES = [
        (STATUS_APPROVED, 'Onaylandı'),
        (STATUS_PENDING, 'Beklemede'),
        (STATUS_REJECTED, 'Reddedildi'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='order_medias')
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='order_medias')
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    reject_reason = models.TextField(blank=True, null=True)

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, '')

    def __str__(self):
        return f"{self.company} - {self.media} ({self.get_status_display()})"