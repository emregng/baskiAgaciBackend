from rest_framework import generics,filters
from .models import Offer
from .serializers import OfferSerializer,OfferListSerializer

class OfferListCreateView(generics.ListCreateAPIView):
    queryset = Offer.objects.filter(is_active=True)
    serializer_class = OfferSerializer

class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.filter(is_active=True)
    serializer_class = OfferSerializer



class OfferListView(generics.ListAPIView):
    queryset = Offer.objects.filter(is_active=True)
    serializer_class = OfferListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['owner__email', 'category__name', 'status','name']
    ordering_fields = ['created_at', 'total_price']
    ordering = ['-created_at']