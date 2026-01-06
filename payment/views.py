from decimal import Decimal
import hashlib
from django.shortcuts import redirect
import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
import hmac
import base64
import urllib
from .models import Payment
from packages.models import Package, UserPackage
from datetime import datetime, timedelta,date
from rest_framework import generics, filters
from .serializers import PaymentSerializer


PAYONTR_SERVICE_URL = "https://sbx-api.payon.tr/integration"
PAYONTR_PUBLIC_KEY = "P0O43NVXNCWTM3IO8PVKN7R8P04LZ0JH"
PAYONTR_PRIVATE_KEY = "Y1EZYDPVI2QZY086XV21VCA2EM8IHNOV"
SUCCESS_PAGE_URL = "http://localhost:5174/success-page"
ERROR_PAGE_URL = "http://localhost:5174/error-payment"
POST_BACK_URL = "http://127.0.0.1:8000/payment/callback/"

def calculate_posment_hash(card_no: str, product_price: str, private_key: str) -> str:
    clean_card_no = card_no.strip()
    clean_price = product_price.strip()
    data_to_hash = f"{clean_card_no}{clean_price}"

    hmac_obj = hmac.new(private_key.encode(), data_to_hash.encode(), hashlib.sha256)
    hex_string = hmac_obj.hexdigest()

    utf8_bytes = hex_string.encode('utf-8')
    base64_hash = base64.b64encode(utf8_bytes).decode('utf-8')
    return base64_hash


def format_to_ext_id(dt=None):
    if dt is None:
        dt = datetime.utcnow()
    return dt.strftime('%Y%m%d%H%M%S')

@api_view(['POST'])
@permission_classes([AllowAny])
def start_3d_payment(request):
    payment = request.data.get("Payment")
    card_no = payment.get("CardNo") if payment else None
    product_price = None
    if payment and payment.get("Products"):
        product_price = str(payment["Products"][0].get("Price"))
    private_key = PAYONTR_PRIVATE_KEY

    if not payment or not card_no or not product_price or not private_key:
        return Response(
            {'success': False, 'error': 'Payment, CardNo, ProductPrice veya PrivateKey eksik.'},
            status=400
        )

    for product in payment.get("Products", []):
        product["Price"] = int(product["Price"])
        product["Count"] = int(product.get("Count", 1))

    hash_val = calculate_posment_hash(card_no, product_price, private_key)
    ext_id = format_to_ext_id()

    user = request.user if request.user.is_authenticated else None
    amount_tl = Decimal(product_price) / 100
    payment_obj = Payment.objects.create(
        user=user,
        amount=amount_tl,
        status='pending'
    )
    payment["ExtId"] = ext_id
    payment["Id"] = payment_obj.id
    payment["PostBackUrl"] = POST_BACK_URL
    payload = {
        "PublicKey": PAYONTR_PUBLIC_KEY,
        "Id": payment_obj.id,
        "Hash": hash_val,
        "Payment": payment, 
    }

    resp = requests.post(
        f"{PAYONTR_SERVICE_URL}/start3dpayment",
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        timeout=30
    )

    try:
        resp_data = resp.json()
    except Exception:
        return Response(
            {'success': False, 'error': 'PayOnTR geçersiz yanıt döndü'},
            status=502
        )
    if resp.status_code == 200:
        data = resp_data.get("data")
        if isinstance(data, dict):
            payon_id = data.get("payonId")
            payment_obj.payontr_transaction_id = str(payon_id)
            payment_obj.save()
            return Response({
                "success": True,
                "payonId": data.get("payonId"),
                "approvmentUrl": data.get("approvmentUrl"),
                "payment_id": payment_obj.id,
                "amount": str(payment_obj.amount)
            })
        else:
            error_message = resp_data.get("clientMessage") or resp_data.get("description") or "PayOnTR 'data' alanı beklenmiyor"
            return Response({
                "success": False,
                "error": error_message,
                "detail": resp_data
            }, status=400)



@api_view(['POST'])
@permission_classes([AllowAny])
def payment_callback(request):
    data = request.data
    transaction_id = data.get("PaymentId")
    success = data.get("Success")
    bank_desc = data.get("BankDesc", "")

    if not transaction_id or success is None:
        return Response({"success": False, "error": "Eksik parametre"}, status=400)

    try:
        payment = Payment.objects.get(payontr_transaction_id=transaction_id)
    except Payment.DoesNotExist:
        return Response({"success": False, "error": "Payment not found"}, status=404)

    if success in ["True", True, "1", 1]:
        payment.status = "success"
        payment.description = bank_desc
        payment.save()

        package_name = "Premium Paket"
        if package_name:
            try:
                package = Package.objects.get(name=package_name)
                UserPackage.objects.create(
                    user=payment.user,
                    package=package,
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=365),
                    is_active=True
                )
            except Package.DoesNotExist:
                pass

        return redirect(SUCCESS_PAGE_URL)
    else:
        payment.status = "failed"
        payment.description = bank_desc
        payment.save()
        bank_desc_encoded = urllib.parse.quote(bank_desc)
        return redirect(f"{ERROR_PAGE_URL}?status=failed&payment_id={payment.id}&message={bank_desc_encoded}")
    

class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.select_related('user').all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        print('status',status)
        if status == 'success':
            queryset = queryset.filter(status='success')
        elif status == 'failed':
            queryset = queryset.filter(status='failed')
        
        return queryset
       