from django.urls import path
from .views import upload_media

urlpatterns = [
    path('upload-media/', upload_media, name='upload_media'),
]