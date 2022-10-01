from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='accounts'),
    
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('reset-password-validate/<uidb64>/<token>', views.reset_password_validate, name='reset-password-validate'),
    path('reset-password/', views.reset_password, name='reset-password'),
 
    path('my-orders/', views.my_orders, name='my-orders'),
    path('edit-profile/', views.edit_profile, name='edit-profile'),
    path('change-password/', views.change_password, name='change-password'),
    path('order-details/<int:order_id>/', views.order_details, name='order-details'),
]
