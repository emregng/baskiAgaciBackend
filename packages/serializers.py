from rest_framework import serializers
from packages.models import UserPackage, Package

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ('id', 'name', 'price', 'content')

class UserPackageSerializer(serializers.ModelSerializer):
    package_id = serializers.IntegerField(write_only=True)
    start_date = serializers.DateField(required=False)
    package = PackageSerializer(read_only=True)

    class Meta:
        model = UserPackage
        fields = ('id', 'package', 'package_id', 'start_date', 'end_date', 'is_active')
        extra_kwargs = {
            'package': {'required': False, 'allow_null': True},
            'end_date': {'required': False, 'allow_null': True},
        }

    def validate(self, data):
        try:
            package = Package.objects.get(id=data['package_id'], is_active=True)
        except Package.DoesNotExist:
            raise serializers.ValidationError({'package_id': 'Paket bulunamadı.'})
        data['package'] = package
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        package = validated_data['package']
        from datetime import date, timedelta

        start_date = validated_data.get('start_date', date.today())
        end_date = start_date + timedelta(days=365)

        # Eğer kullanıcıda zaten aktif ve ücretsiz bir paket varsa yeni oluşturma
        if package.price == 0:
            exists = UserPackage.objects.filter(
                user=user,
                package__price=0,
                is_active=True
            ).exists()
            if exists:
                raise serializers.ValidationError({'message': 'Zaten aktif ücretsiz paketiniz var.'})

            UserPackage.objects.filter(user=user, is_active=True).update(is_active=False)
            user_package = UserPackage.objects.create(
                user=user,
                package=package,
                start_date=start_date,
                end_date=end_date,
                is_active=True
            )
            return user_package
        else:
            raise serializers.ValidationError({'package_id': 'Ödeme tamamlanmadan paket eklenemez.'})