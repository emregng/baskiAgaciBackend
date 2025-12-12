from rest_framework import serializers
from .models import User,Sector,City, District

from company.models import Company
from packages.serializers import UserPackageSerializer



class NullableIntegerField(serializers.IntegerField):
    def to_internal_value(self, data):
        if data in ("", None):
            return None
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    user_packages = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'is_superuser', 'groups',
            'first_name', 'last_name', 'user_packages'
        )
        read_only_fields = ('id', 'is_superuser')

    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]

    def get_user_packages(self, obj):
        # Sadece aktif olan paket(ler)i döndür
        active_packages = obj.user_packages.filter(is_active=True)
        return UserPackageSerializer(active_packages, many=True).data



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    companyName = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    fullName = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    companySektor = serializers.CharField(write_only=True)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), required=False, allow_null=True)
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all(), required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = (
            'email', 'username', 'password', 'password_confirm',
            'companyName', 'fullName', 'phone', 'companySektor','city','district'
        )
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": ["Şifreler eşleşmiyor."]})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": ["Bu email ile kayıtlı bir kullanıcı var."]})
        if User.objects.filter(phone=data['phone']).exists():
            raise serializers.ValidationError({"phone": ["Bu telefon numarası ile kayıtlı bir kullanıcı var."]})
        return data
    
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        full_name = validated_data.pop('fullName')
        city = validated_data.pop('city', None)
        district = validated_data.pop('district', None)
        first_name, last_name = '', ''
        if ' ' in full_name:
            first_name, last_name = full_name.split(' ', 1)
        else:
            first_name = full_name

        # Sektörü bul veya oluştur
        sector, _ = Sector.objects.get_or_create(name=validated_data.pop('companySektor'))

        # Şirketi oluştur
        company = Company.objects.create(
            name=validated_data.pop('companyName'),
            sector=sector
        )

        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username', validated_data['email']),
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
            is_phone_verified=False,
            is_email_verified=False,
            city=city,
            district=district
        )
        user.phone = validated_data['phone']
        user.company = company
        user.save()

        # SMS kodu üret
        import random
        from django.utils import timezone
        code = str(random.randint(100000, 999999))
        user.sms_code = code
        user.sms_code_created = timezone.now()
        user.save()
        # SMS gönderimini burada entegre edebilirsiniz

        return user
    




class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ('id', 'name')

class CitySerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True, read_only=True)

    class Meta:
        model = City
        fields = ('id', 'name', 'code', 'districts')
    