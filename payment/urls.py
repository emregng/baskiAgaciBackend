from django.urls import path
from .views import  PaymentListView, start_3d_payment,payment_callback

urlpatterns = [
    path('start3dpayment/', start_3d_payment, name='start_3d_payment'),
    path('callback/', payment_callback, name='payment_callback'),  # <-- callback endpoint'i
    path('list/', PaymentListView.as_view(), name='payment_list'),


]