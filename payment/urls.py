from django.urls import path
from .views import  start_3d_payment

urlpatterns = [
    path('start3dpayment/', start_3d_payment, name='start_3d_payment'),
]