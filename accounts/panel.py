from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, filters
from .models import User
from .serializers import UserSerializer, RegisterSerializer
from company.models import CompanyMedia
from company.serailizers import CompanyMediaSerializer

class ActiveUsersListView(generics.ListAPIView):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone', 'company__name']
    ordering_fields = ['date_joined', 'email']
    ordering = ['-date_joined']

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        if status == 'Aktif':
            queryset = queryset.filter(user_active=True)
        elif status == 'Pasif':
            queryset = queryset.filter(user_active=False)
        return queryset


@api_view(['POST'])
def create_user(request):
    send_sms = request.data.get('send_sms', True)
    serializer = RegisterSerializer(data=request.data, context={'send_sms': send_sms})
    if serializer.is_valid():
        user = serializer.save()
        return Response({'success': True, 'user': UserSerializer(user).data})
    return Response({'success': False, 'errors': serializer.errors}, status=400)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_status(request):
    user_id = request.data.get('id')
    is_active = request.data.get('is_active')
    if user_id is None or is_active is None:
        return Response({'success': False, 'message': 'Eksik parametre.'}, status=400)
    try:
        user = User.objects.get(id=user_id)
        user.user_active = is_active
        user.save()
        return Response({'success': True, 'message': 'Kullanıcı durumu güncellendi.'})
    except User.DoesNotExist:
        return Response({'success': False, 'message': 'Kullanıcı bulunamadı.'}, status=404)
    


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    user_id = request.data.get('id')
    if not user_id:
        return Response({'success': False, 'message': 'Kullanıcı ID gerekli.'}, status=400)
    try:
        user = User.objects.get(id=user_id)
        # Kullanıcıya ait şirketi de sil
        if user.company:
            user.company.delete()
        user.delete()
        return Response({'success': True, 'message': 'Kullanıcı ve şirketi silindi.'})
    except User.DoesNotExist:
        return Response({'success': False, 'message': 'Kullanıcı bulunamadı.'}, status=404)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({'success': False, 'message': 'Kullanıcı bulunamadı.'}, status=404)
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({'success': False, 'message': 'Kullanıcı bulunamadı.'}, status=404)
    serializer = RegisterSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'user': UserSerializer(user).data})
    return Response({'success': False, 'errors': serializer.errors}, status=400)



class CompanyMediaListView(generics.ListAPIView):
    queryset = CompanyMedia.objects.all()
    serializer_class = CompanyMediaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company__name', 'media__url']
    ordering_fields = ['created_at', 'order']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        if status == '0':
            queryset = queryset.filter(status=CompanyMedia.STATUS_APPROVED)
        elif status == '1':
            queryset = queryset.filter(status=CompanyMedia.STATUS_PENDING)
        elif status == '2':
            queryset = queryset.filter(status=CompanyMedia.STATUS_REJECTED)
        return queryset
    

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_image_status(request):
    media_id = request.data.get('id')
    status = request.data.get('status')
    reject_reason = request.data.get('reject_reason', '')

    if media_id is None or status is None:
        return Response({'success': False, 'message': 'Eksik parametre.'}, status=400)
    try:
        media = CompanyMedia.objects.get(id=media_id)
        media.status = status
        media.reject_reason = reject_reason
        media.save()
        return Response({'success': True, 'message': 'Resim durumu güncellendi.'})
    except CompanyMedia.DoesNotExist:
        return Response({'success': False, 'message': 'Resim bulunamadı.'}, status=404)