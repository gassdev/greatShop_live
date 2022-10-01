from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('remove-cart/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove-cart'),
    path('remove-cart-item/<int:product_id>/<int:cart_item_id>/', views.remove_cart_item, name='remove-cart-item'),

    path('checkout/', views.checkout, name='checkout'),

]
