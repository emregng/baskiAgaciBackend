from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'payontr_transaction_id',
            'user_full_name',
            'amount',
            'status',
            'created_at',
        ]

    def get_user_full_name(self, obj):
        full_name = f"{obj.user.first_name or ''} {obj.user.last_name or ''}".strip()
        return full_name if full_name else obj.user.email