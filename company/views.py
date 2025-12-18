from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Company, CompanyMedia
from .serailizers import CompanyMediaSerializer,CompanyMediaSimpleSerializer
from media.models import Media

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_company_media(request):
    serializer = CompanyMediaSerializer(data=request.data, context={'request': request})
    print("Serializer data:", request.data)
    if serializer.is_valid():
        created_medias = serializer.save()
        response_serializer = CompanyMediaSerializer(created_medias, many=True)
        return Response({'success': True, 'data': response_serializer.data})
    # Hataları detaylı döndür
    return Response({
        'success': False,
        'errors': serializer.errors,
        'detail': 'Geçersiz veri, lütfen alanları kontrol edin.'
    }, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_company_media(request):
    user = request.user
    if not hasattr(user, 'company') or user.company is None:
        return Response({'success': False, 'error': 'Kullanıcının bir şirketi yok.'}, status=404)
    medias = CompanyMedia.objects.filter(company=user.company).order_by('order')
    serializer = CompanyMediaSimpleSerializer(medias, many=True)
    return Response(serializer.data)