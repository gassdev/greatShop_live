from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages, auth
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from orders.models import Order, OrderProduct

from .models import Account, UserProfile
from carts.models import Cart, CartItem
from carts.views import _cart_id
from .forms import RegistrationForm, UserForm, UserProfileForm
from greatShop.settings import (
    MAILJET_API_KEY, MAILJET_SECRET_KEY, 
    MAILJET_TEMPLATE_ID, MAILJET_SENDER_EMAIL,
    PASSWORD_RESET_TEMPLATE_ID
)

from mailjet_rest import Client
import requests



def _send_account_activation_mail_with_mailjet(to_email, current_site, activation_link):
    mailJet = Client(
        auth=(MAILJET_API_KEY, MAILJET_SECRET_KEY),
        version="v3.1"
    )
    data = {
    'Messages': [
            {
                "From": {
                    "Email": MAILJET_SENDER_EMAIL,
                    "Name": "Great Shop Account Activation"
                },
                "To": [
                    {
                        "Email": to_email,
                    }
                ],
                "TemplateID": MAILJET_TEMPLATE_ID,
                "TemplateLanguage": True,
                "Subject": "Email Activation",
                "Variables": {
        "current_site": f"{current_site}",
        "confirmation_link": f"{activation_link}"
    }
            }
        ]
    }
    result = mailJet.send.create(data=data)
    return result.status_code


def _send_password_reset_link_mail_with_mailjet(to_email, fullname, reset_link):
    mailJet = Client(
        auth=(MAILJET_API_KEY, MAILJET_SECRET_KEY),
        version="v3.1"
    )
    data = {
    'Messages': [
            {
                "From": {
                    "Email": MAILJET_SENDER_EMAIL,
                    "Name": "Great Shop Password Reset Link"
                },
                "To": [
                    {
                        "Email": to_email,
                    }
                ],
                "TemplateID": PASSWORD_RESET_TEMPLATE_ID,
                "TemplateLanguage": True,
                "Subject": "Password Reset Link",
                "Variables": {
                    "resetlink": reset_link,
                    "fullname": fullname
                }
            }
        ]
    }
    result = mailJet.send.create(data=data)
    return result.status_code

def register(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            
            user: Account = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=email.split("@")[0],
                password=password,
            )
            user.phone_number = phone_number
            user.save()
            
            # Create user profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.picture = 'default/default.jpg'
            profile.save()
            
            # user activation
            current_site = get_current_site(request)
            domain = f"http://{current_site}"
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activattion_link = f"<a style='color:white;text-decoration:none;' href='{domain}{reverse('activate', kwargs={'uidb64':uid, 'token':token})}'>Activate now</a>"
            status_code =_send_account_activation_mail_with_mailjet(email, domain, activattion_link)
            print(status_code)
            
            # messages.success(request, 'An activation link has been sent to your email address!')
            return redirect('/accounts/login?command=verification&email='+email)
        else:
            # print(form.errors)
            pass
    else:
        form=RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def activate(request: HttpRequest, uidb64=None, token=None):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user: Account = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account has been activated.')
        return redirect('login')
    else:
        messages.success(request, 'Invalid activation link')
        return redirect('register')


def login(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('home')
    email = ''
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = auth.authenticate(request, email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(
                    cart=cart
                ).exists()
                if is_cart_item_exists:
                    cart_items = CartItem.objects.filter(cart=cart)
                    
                    # Getting the product variation by cart_id
                    product_variation = []
                    for item in cart_items:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                        
                    # Get the cart items from the user to access his product variations
                    cart_items: CartItem = CartItem.objects.filter(
                    user=user
                    )
            
                    ex_var_list=[]
                    id = []
                    for item in cart_items:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_items = CartItem.objects.filter(cart=cart)
                            for item in cart_items:
                                item.user=user
                                item.save()
                            
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # print('query --> ', query)
                params = dict(x.split('=') for x in query.split('&'))
                # print(params)
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials.')
            return render(request, 'accounts/login.html', {'email':email})
    context = {
        'email':email,
    }
    return render(request, 'accounts/login.html', context)


@login_required
def dashboard(request: HttpRequest):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    orders_count=orders.count()
    context = {
        'orders_count': orders_count
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
def logout(request: HttpRequest):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')

def forgot_password(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user: Account = Account.objects.get(email__exact=email)
            
            # Reset Password Email
            current_site = get_current_site(request)
            domain = f"http://{current_site}"
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            resetlink = f"<a style='color:white;text-decoration:none;' href='{domain}{reverse('reset-password-validate', kwargs={'uidb64':uid, 'token':token})}'>Reset Password</a>"
            status_code =_send_password_reset_link_mail_with_mailjet(
                email,
                f"{user.first_name} {user.last_name}",
                resetlink
                )
            if status_code == 200:
                
                messages.success(
                    request,
                    'Password reset link has been sent to your email address.'
                )
                return redirect('login')
        else:
            messages.error(request, f'An account with address email {email} does not exist.')
            return redirect('forgot-password')
    return render(request, 'accounts/forgot_password.html')

def reset_password_validate(request: HttpRequest, uidb64=None, token=None):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user: Account = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.success(
            request,
            'Please reset your password'
        )
        return redirect('reset-password')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('login')
        
def reset_password(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user: Account = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(
                request,
                'You have successfully reseted your password.'
            )
            return redirect('login')
        else:
            messages.error(
                request,
                'Password do not match'
            )
            return redirect('reset-password')
    return render(request, 'accounts/reset_password.html')

@login_required(login_url='login')
def my_orders(request: HttpRequest):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context={
        'orders':orders,
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url='login')
def edit_profile(request: HttpRequest):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,
                             'Your profile has been updated!')
            return redirect('edit-profile')
    else:
        user_form=UserForm(instance=request.user)
        profile_form=UserProfileForm(instance=user_profile)
        
    context={
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': user_profile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request: HttpRequest):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        
        user: Account = Account.objects.get(username__exact=request.user.username)
        
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request,
                                 'Password successfully updated!')
                return redirect('change-password')
            else:
                messages.error(request,
                               'Please enter valid current password')
                return redirect('change-password')
        else:
            messages.error(
                request,
                'Password does not match'
            )
            return redirect('change-password')
    return render(request, 'accounts/change_password.html')

@login_required(login_url='login')
def order_details(request: HttpRequest, order_id=None):
    try:
        subtotal=0
        order_details = OrderProduct.objects.filter(
            order__order_number=order_id
        )
        order = Order.objects.get(order_number=order_id)
        for i in order_details:
            subtotal += i.quantity*i.product_price
        context = {
            'order_details': order_details,
            'order': order,
            'subtotal': subtotal,
        }
        return render(request, 'accounts/order_details.html', context)
    except:
        return redirect('my-orders')