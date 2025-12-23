from rest_framework import serializers
from .models import Offer, Category

class OfferDetailsField(serializers.DictField):
    child = serializers.CharField(allow_blank=True)


class OfferDetailItemSerializer(serializers.Serializer):
    value = serializers.CharField(allow_blank=True, required=False)
    price = serializers.FloatField()



class OfferSerializer(serializers.ModelSerializer):
    details = serializers.ListField()

    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    total_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Offer
        fields = ['id', 'name','category', 'owner', 'status', 'total_price', 'details', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at', 'status']

    def create(self, validated_data):
        raw_details = validated_data.pop('details', [])
        # Her item'a price ekle
        for item in raw_details:
            item['price'] = self.get_price_for_field(item.get("name"), item.get("value"))
        validated_data['details'] = raw_details  # Liste olarak kaydet!
        validated_data['owner'] = self.context['request'].user
        return Offer.objects.create(**validated_data)

    def get_price_for_field(self, key, value):
        return 100.0


class OfferListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    owner = serializers.StringRelatedField()
    status_label = serializers.CharField(source='get_status_display', read_only=True)


    class Meta:
        model = Offer
        fields = ['id', 'category','category_name', 'owner', 'status', 'name','status_label','total_price', 'created_at']