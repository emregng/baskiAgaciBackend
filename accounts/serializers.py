from rest_framework import serializers

from packages.models import Package,UserPackage
from payment.models import Payment
from .models import User,Sector,City, District,PaymentType

from company.models import Company
from packages.serializers import UserPackageSerializer
import requests
from django.http.response import HttpResponse,JsonResponse
import xml.etree.ElementTree as etree
import xml.etree.ElementTree as ET
import re
import random
from django.utils import timezone
from datetime import date, timedelta

def CDATA(text=None):
    element = ET.Element('![CDATA[')
    element.text = text
    return element


def send_sms(gsm1):
    url = "https://api.1sms.com.tr/api/smspost/v1"
    headers = {'content-type': 'text/xml;charset=utf-8'}
    root = ET.Element("sms")

    ET.SubElement(root, "username").text = "Akinfurkan"
    ET.SubElement(root, "password").text = "19eb5913787054074b2264797b9f52c5"
    ET.SubElement(root, "header").text = "FUA MATBAA"
    ET.SubElement(root, "validity").text = "2880"
    ET.SubElement(root, "sendDateTime").text = "2015.7.23.9.30.0"

    messages = ET.SubElement(root, "messages")
    for item in gsm1:
        mb = ET.SubElement(messages, "mb")
        no = ET.SubElement(mb, "no")
        msg = ET.SubElement(mb, "msg")
        no.text = item['gsm_1']
        msg.text = None
        msg.append(ET.Comment(f"[CDATA[{item['icerik']}]]"))

    xml_str = ET.tostring(root, encoding='unicode')
    
    xml_str = re.sub(r'<msg><!--\[CDATA\[(.*?)\]\]--></msg>', r'<msg><![CDATA[\1]]></msg>', xml_str)
    try:
        response = requests.post(url, data=xml_str.encode('utf-8'), headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        # Burada loglama da yapabilirsin
        return f"SMS gönderimi başarısız: {str(e)}"



class NullableIntegerField(serializers.IntegerField):
    def to_internal_value(self, data):
        if data in ("", None):
            return None
        return super().to_internal_value(data)

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = ('id', 'name')

class CompanySerializer(serializers.ModelSerializer):
    sector = SectorSerializer(read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'address', 'phone_number', 'email', 'sector','taxOffice','taxNumber','social_media')




class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ('id', 'name')

class CitySerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True, read_only=True)

    class Meta:
        model = City
        fields = ('id', 'name', 'code', 'districts')
        


class PaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentType
        fields = ['id', 'name', 'order']


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    user_packages = serializers.SerializerMethodField()
    city = CitySerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    company = CompanySerializer(read_only=True)
    payment_type = PaymentTypeSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'is_superuser', 'groups',
            'first_name', 'last_name', 'phone', 'city', 'district',
            'user_packages', 'company','is_active','payment_type','user_active','date_joined'
        )
        read_only_fields = ('id', 'is_superuser')

    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]

    def get_user_packages(self, obj):
        active_packages = obj.user_packages.filter(is_active=True)
        result = []
        today = date.today()
        for up in active_packages:
            serializer = UserPackageSerializer(up)
            data = serializer.data
            # start_date ve end_date string olarak gelir, date objesine çevir
            try:
                end_date = up.end_date
                kalan_gun = (end_date - today).days
            except Exception:
                kalan_gun = None
            data['remaining_days'] = kalan_gun
            result.append(data)
        return result




class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=False, allow_blank=True)
    password_confirm = serializers.CharField(write_only=True, min_length=8, required=False, allow_blank=True)
    companyName = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    fullName = serializers.CharField(write_only=True)
    phone = serializers.CharField()
    companySektor = serializers.CharField(write_only=True)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), required=False, allow_null=True)
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all(), required=False, allow_null=True)
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)
    taxOffice = serializers.CharField(write_only=True, required=False, allow_blank=True)
    socialMedia = serializers.CharField(write_only=True, required=False, allow_blank=True)
    paymentType = serializers.PrimaryKeyRelatedField(queryset=PaymentType.objects.all(), write_only=True, required=False, allow_null=True)
    package = serializers.PrimaryKeyRelatedField(queryset=Package.objects.all(), write_only=True, required=False, allow_null=True)
    class Meta:
        model = User
        fields = (
            'email', 'username', 'password', 'password_confirm',
            'companyName', 'fullName', 'phone', 'companySektor','city','district','address','taxOffice', 'socialMedia',
            'paymentType', 'package'
        )
    
    def validate(self, data):
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        # Sadece create işlemi için şifre zorunlu
        if not self.instance:
            if not password or not password_confirm:
                raise serializers.ValidationError({
                    "password": ["Şifre zorunlu."],
                    "password_confirm": ["Şifre tekrarı zorunlu."]
                })
            if password != password_confirm:
                raise serializers.ValidationError({"password_confirm": ["Şifreler eşleşmiyor."]})
        else:
            # Update ise, şifre alanları varsa kontrol et
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
        tax_office = validated_data.pop('taxOffice', '')
        social_media = validated_data.pop('socialMedia', '')
        address = validated_data.pop('address', '')
        payment_type = validated_data.pop('paymentType', None)
        package = validated_data.pop('package', None)
        # Sektörü bul veya oluştur
        sector, _ = Sector.objects.get_or_create(id=validated_data.pop('companySektor'))

       # Şirketi oluştur
        company_name = validated_data.pop('companyName')
        if Company.objects.filter(name__iexact=company_name).exists():
            raise serializers.ValidationError({"companyName": "Bu isimde bir şirket zaten mevcut."})

        company = Company.objects.create(
            name=company_name,
            sector=sector,
            taxOffice=tax_office,
            social_media=social_media,
            is_active=True,
            address=address
)
  
        code = str(random.randint(100000, 999999))
        is_phone_verified = False

        send_sms_flag = self.context.get('send_sms', True)
    
        if send_sms_flag:
            is_phone_verified = False
            user_active = False
            sms_data = [{
                'gsm_1': validated_data['phone'],
                'icerik': f"Merhaba, Baskı Ağacı'na hoş geldiniz! Hesabınızı doğrulamak için onay kodunuz: {code}. Lütfen bu kodu kimseyle paylaşmayınız."
            }]
            sms_result = send_sms(sms_data)
            sms_code_length = len(sms_result.strip())
            if sms_code_length < 3:
                raise serializers.ValidationError({"sms": "SMS gönderimi başarısız. Lütfen telefon numaranızı kontrol edin."})
        else:
            is_phone_verified = True
            user_active = True
        
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username', validated_data['email']),
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
          
            is_email_verified=False,
            city=city,
            district=district,
            payment_type=payment_type,
            user_active = user_active
            
        )
        user.phone = validated_data['phone']
        user.company = company
        user.sms_code = code
        user.sms_code_created = timezone.now()
        user.save()
        if package:
            UserPackage.objects.create(
                user=user,
                package=package,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=365),
                is_active=True
            )
            if getattr(package, "name", "").lower() == "premium paket":
                Payment.objects.create(
                    user=user,
                    amount=5000,
                    status='success'
                )
        return user

     
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        password_confirm = validated_data.pop('password_confirm', None)
        company_name = validated_data.get('companyName', instance.company.name if instance.company else '')
        company_sector_id = validated_data.get('companySektor', instance.company.sector.id if instance.company and instance.company.sector else None)
        address = validated_data.get('address', instance.company.address if instance.company else '')
        tax_office = validated_data.get('taxOffice', instance.company.taxOffice if instance.company else '')
        social_media = validated_data.get('socialMedia', instance.company.social_media if instance.company else '')

        # Sektör id'si ile sektörü bul
        sector = None
        if company_sector_id:
            sector = Sector.objects.filter(id=company_sector_id).first()
            if not sector:
                raise serializers.ValidationError({"companySektor": "Geçersiz sektör id'si."})

        if instance.company:
            instance.company.name = company_name
            if sector:
                instance.company.sector = sector
            instance.company.address = address
            instance.company.taxOffice = tax_office
            instance.company.social_media = social_media
            instance.company.save()
        else:
            company = Company.objects.create(
                name=company_name,
                sector=sector,
                address=address,
                taxOffice=tax_office,
                social_media=social_media,
                is_active=True
            )
            instance.company = company

        full_name = validated_data.get('fullName', instance.full_name)
        instance.full_name = full_name
        instance.first_name = full_name.split(' ')[0] if full_name else instance.first_name
        instance.last_name = ' '.join(full_name.split(' ')[1:]) if full_name and ' ' in full_name else instance.last_name
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.city = validated_data.get('city', instance.city)
        instance.district = validated_data.get('district', instance.district)
        payment_type = validated_data.get('paymentType', None)
        if payment_type:
            instance.payment_type = payment_type

        if password:
            instance.set_password(password)
        instance.save()

        # Paket güncellemesi (varsa)
        package = validated_data.get('package', None)
        if package:
            from packages.models import UserPackage
            from datetime import date, timedelta
            UserPackage.objects.filter(user=instance, is_active=True).update(is_active=False)
            UserPackage.objects.create(
                user=instance,
                package=package,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=365),
                is_active=True
            )

        return instance
    
    



