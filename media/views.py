from django.shortcuts import render

# Create your views here.
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from .models import Media
from .serializers import MediaSerializer
from PIL import Image
import time

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_media(request):
    file = request.FILES['file']
    filename = file.name
    # Eşsiz dosya ismi oluştur
    user_id = request.user.id
    timestamp = int(time.time())
    ext = os.path.splitext(filename)[1]
    unique_filename = f"{user_id}_{timestamp}{ext}"
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)

    # Dosyayı kaydet
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    # WebP'ye çevir
    webp_filename = f"{user_id}_{timestamp}.webp"
    webp_path = os.path.join(upload_dir, webp_filename)
    try:
        img = Image.open(file_path)
        img.save(webp_path, 'webp')
        webp_url = request.build_absolute_uri(settings.MEDIA_URL + 'uploads/' + webp_filename)
    except Exception:
        webp_url = None

    url = request.build_absolute_uri(settings.MEDIA_URL + 'uploads/' + unique_filename)

    media = Media.objects.create(
        url=url,
        webp_url=webp_url,
        original_filename=filename,
        is_active=True
    )
    return Response(MediaSerializer(media).data)