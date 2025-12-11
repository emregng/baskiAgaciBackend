from django.db import models
from accounts.models import User

class Package(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    content = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class UserPackage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_packages')
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='user_packages')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} - {self.package.name}"