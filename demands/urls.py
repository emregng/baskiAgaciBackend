from django.urls import path
from . import views

urlpatterns = [
    path('offers/', views.OfferListCreateView.as_view(), name='offer-list-create'),
    path('offers/<int:pk>/', views.OfferDetailView.as_view(), name='offer-detail'),
    path('offers/list/', views.OfferListView.as_view(), name='offer-list'),
]