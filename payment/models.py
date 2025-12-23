from django.db import models
from accounts.models import User

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('success', 'Başarılı'),
        ('failed', 'Başarısız'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    payontr_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response_code = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.amount} TL - {self.status}"