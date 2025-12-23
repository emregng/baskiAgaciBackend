import hashlib
import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
import hmac
import base64



PAYONTR_SERVICE_URL = "https://sbx-api.payon.tr/integration"
PAYONTR_PUBLIC_KEY = "P0O43NVXNCWTM3IO8PVKN7R8P04LZ0JH"
PAYONTR_PRIVATE_KEY = "Y1EZYDPVI2QZY086XV21VCA2EM8IHNOV"

def calculate_posment_hash(card_no: str, product_price: str, private_key: str) -> str:
    clean_card_no = card_no.strip()
    clean_price = product_price.strip()
    data_to_hash = f"{clean_card_no}{clean_price}"

    # HMAC SHA256
    hmac_obj = hmac.new(private_key.encode(), data_to_hash.encode(), hashlib.sha256)
    hex_string = hmac_obj.hexdigest()

    # Hex -> UTF8 -> Base64
    utf8_bytes = hex_string.encode('utf-8')
    base64_hash = base64.b64encode(utf8_bytes).decode('utf-8')
    return base64_hash



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

    import json
    hash_val = calculate_posment_hash(card_no, product_price, private_key)

    payload = {
        "PublicKey": PAYONTR_PUBLIC_KEY,
        "Hash": hash_val,
        "Payment": payment
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
    print("PayOnTR start3dpayment response:", resp.status_code, resp.text)

    try:
        resp_data = resp.json()
    except Exception:
        return Response(
            {'success': False, 'error': 'PayOnTR geçersiz yanıt döndü'},
            status=502
        )
    if resp.status_code == 200:
        data = resp_data.get("data", {})
        return Response({
            "success": True,
            "payonId": data.get("payonId"),
            "approvmentUrl": data.get("approvmentUrl"),
        })

    if isinstance(resp_data, dict):
        error_message = resp_data.get("clientMessage") or resp_data.get("description") or "Ödeme başlatılamadı"
        detail = resp_data
    else:
        error_message = "PayOnTR servisinden beklenmeyen yanıt"
        detail = resp_data

    return Response({
        "success": False,
        "error": error_message,
        "detail": detail
    }, status=400)