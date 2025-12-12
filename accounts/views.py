from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User,Sector,City,District
from .serializers import RegisterSerializer, UserSerializer,CitySerializer,DistrictSerializer
from django.utils import timezone
import random
from datetime import timedelta
from .serializers import CitySerializer,DistrictSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Kayıt başarılı',
            'user': UserSerializer(user).data,
            'token': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'success': False,
            'message': 'Email ve şifre gereklidir'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=email, password=password)
    
    if user is not None:
        if not user.is_active:
            return Response({
                'success': False,
                'message': 'Hesabınız devre dışı bırakılmış'
            }, status=status.HTTP_403_FORBIDDEN)
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'success': True,
            'message': 'Giriş başarılı',
            'user': UserSerializer(user).data,
            'token': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Email veya şifre hatalı'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        print('Test')
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'success': True,
            'message': 'Başarıyla çıkış yapıldı'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print('Logout error:', str(e))
        return Response({
            'success': False,
            'message': 'Çıkış yapılırken bir hata oluştu'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def sektor(request):
    sektor = Sector.objects.filter(is_active=True).values('id', 'name')
    return Response(list(sektor))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_sms_code(request):
    user = request.user
    code = str(random.randint(100000, 999999))
    user.sms_code = code
    user.sms_code_created = timezone.now()
    user.save()
    # Burada gerçek SMS gönderimi yapılmalı (ör: Twilio, Netgsm, vs.)
    print(f"SMS code for {user.phone_number}: {code}")  # Sadece test için
    return Response({'success': True, 'message': 'SMS kodu gönderildi.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_sms_code(request):
    user = request.user
    code = request.data.get('code')
    if not code:
        return Response({'success': False, 'message': 'Kod gerekli.'}, status=status.HTTP_400_BAD_REQUEST)
    if not user.sms_code or not user.sms_code_created:
        return Response({'success': False, 'message': 'Kod gönderilmemiş.'}, status=status.HTTP_400_BAD_REQUEST)
    if timezone.now() > user.sms_code_created + timedelta(minutes=10):
        return Response({'success': False, 'message': 'Kodun süresi doldu.'}, status=status.HTTP_400_BAD_REQUEST)
    if user.sms_code != code:
        return Response({'success': False, 'message': 'Kod yanlış.'}, status=status.HTTP_400_BAD_REQUEST)
    user.is_phone_verified = True
    user.sms_code = None
    user.sms_code_created = None
    user.save()
    return Response({'success': True, 'message': 'Telefon doğrulandı.'})




@api_view(['GET'])
@permission_classes([AllowAny])
def city_list(request):
    cities = City.objects.all().order_by('name')
    serializer = CitySerializer(cities, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def district_list(request, city_id):
    districts = District.objects.filter(city_id=city_id).order_by('name')
    serializer = DistrictSerializer(districts, many=True)
    return Response(serializer.data)