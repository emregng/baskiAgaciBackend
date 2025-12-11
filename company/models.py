from django.db import models

# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    sector = models.ForeignKey('accounts.Sector', on_delete=models.SET_NULL, related_name='companies',null=True,blank=True)

    def __str__(self):
        return self.name