from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Package,UserPackage
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta
from .serializers import UserPackageSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def package_list(request):
    packages = Package.objects.filter(is_active=True)
    data = [
        {
            "id": p.id,
            "name": p.name,
            "price": str(p.price),
            "content": p.content
        }
        for p in packages
    ]
    return Response(data)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_package(request):
    data = request.data.copy()
    data['user'] = request.user.id  # User otomatik eklenmeli
    serializer = UserPackageSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'message': 'Paket başarıyla eklendi.'})
    print('serializer.errors',)
    return Response({'success': False, 'errors': serializer.errors}, status=400)