from django.urls import path
from .views import add_company_media, list_company_media

urlpatterns = [
    path('add-media/', add_company_media, name='add_company_media'),
    path('list-media/', list_company_media, name='list_company_media'),
]