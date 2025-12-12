from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Sector)
admin.site.register(City)
admin.site.register(District)