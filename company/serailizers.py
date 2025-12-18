from rest_framework import serializers
from .models import CompanyMedia

from rest_framework import serializers
from .models import CompanyMedia, Company
from media.models import Media

class CompanyMediaSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    media = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CompanyMedia
        fields = ['id', 'company', 'media', 'status', 'status_label', 'is_active', 'order', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        if not user or not hasattr(user, 'company') or user.company is None:
            raise serializers.ValidationError({'company': 'Kullanıcının bir şirketi yok.'})

        media_list = request.data.get('media', [])
        created_medias = []
        for item in media_list:
            media_id = item.get('media_id')
            order = item.get('order', 0)
            status = item.get('status', CompanyMedia.STATUS_PENDING)
            try:
                media = Media.objects.get(id=media_id)
            except Media.DoesNotExist:
                continue

            # Eğer zaten varsa sadece order ve status güncelle, tekrar ekleme
            try:
                company_media = CompanyMedia.objects.get(company=user.company, media=media)
                company_media.order = order
                company_media.status = status
                company_media.save()
            except CompanyMedia.DoesNotExist:
                company_media = CompanyMedia.objects.create(
                    company=user.company,
                    media=media,
                    status=status,
                    is_active=True,
                    order=order
                )
            created_medias.append(company_media)
        return created_medias
    
class CompanyMediaSimpleSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    class Meta:
        model = CompanyMedia
        fields = ['id', 'url', 'status', 'order']

    def get_url(self, obj):
        return obj.media.url if obj.media and obj.media.url else None

    def get_status(self, obj):
        return obj.status if obj.status is not None else None

    def get_id(self, obj):
        return obj.media.id if obj.media else None