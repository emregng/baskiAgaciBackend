from rest_framework import serializers
from .models import User,Sector,City, District

from company.models import Company
from packages.serializers import UserPackageSerializer



class NullableIntegerField(serializers.IntegerField):
    def to_internal_value(self, data):
        if data in ("", None):
            return None
        return super().to_internal_value(data)




class CompanySerializer(serializers.ModelSerializer):
    sector = serializers.CharField(source='sector.name', read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'address', 'phone_number', 'email', 'sector')

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ('id', 'name')

class CitySerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True, read_only=True)

    class Meta:
        model = City
        fields = ('id', 'name', 'code', 'districts')
        

class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    user_packages = serializers.SerializerMethodField()
    city = CitySerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    company = CompanySerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'is_superuser', 'groups',
            'first_name', 'last_name', 'phone', 'city', 'district',
            'user_packages', 'company'
        )
        read_only_fields = ('id', 'is_superuser')

    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]

    def get_user_packages(self, obj):
        active_packages = obj.user_packages.filter(is_active=True)
        return UserPackageSerializer(active_packages, many=True).data



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    companyName = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    fullName = serializers.CharField(write_only=True)
    phone = serializers.CharField()
    companySektor = serializers.CharField(write_only=True)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), required=False, allow_null=True)
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all(), required=False, allow_null=True)
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'password', 'password_confirm',
            'companyName', 'fullName', 'phone', 'companySektor','city','district','address'
        )
    
    def validate(self, data):
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        if password or password_confirm:
            if password != password_confirm:
                raise serializers.ValidationError({"password_confirm": ["Şifreler eşleşmiyor."]})
        if 'email' in data and User.objects.filter(email=data['email']).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError({"email": ["Bu email ile kayıtlı bir kullanıcı var."]})
        if 'phone' in data and User.objects.filter(phone=data['phone']).exclude(pk=self.instance.pk if self.instance else None).exists():
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
    def update(self, instance, validated_data):
        # Şirket bilgilerini güncelle
        company = instance.company
        if company:
            company.name = validated_data.get('companyName', company.name)
            company.sector, _ = Sector.objects.get_or_create(name=validated_data.get('companySektor', company.sector.name if company.sector else ''))
            print("Updating company sector to:", company.sector)
            company.address = validated_data.get('address', company.address)
            company.save()
        else:
            # Eğer kullanıcıya şirket atanmamışsa yeni oluştur
            sector, _ = Sector.objects.get_or_create(name=validated_data.get('companySektor', ''))
            company = Company.objects.create(
                name=validated_data.get('companyName', ''),
                sector=sector
            )
            instance.company = company

        # Kullanıcı bilgilerini güncelle
        instance.full_name = validated_data.get('fullName', instance.full_name)
        instance.first_name = validated_data.get('fullName', instance.first_name).split(' ')[0]
        instance.last_name = ' '.join(validated_data.get('fullName', instance.last_name).split(' ')[1:]) if ' ' in validated_data.get('fullName', '') else instance.last_name
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.city = validated_data.get('city', instance.city)
        instance.district = validated_data.get('district', instance.district)
        instance.save()
        return instance
    
    





    