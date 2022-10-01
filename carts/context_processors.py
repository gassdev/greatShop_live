from django.http import HttpRequest

from greatShop.settings import PAYPAL_CLIENT_ID
from .models import Cart, CartItem
from .views import _cart_id

def counter(request: HttpRequest):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart=cart[:1])
            
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)

def get_paypal_client_id(request: HttpRequest):
    return dict(PAYPAL_CLIENT_ID=PAYPAL_CLIENT_ID)