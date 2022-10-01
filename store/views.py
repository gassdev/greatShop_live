from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from carts.models import CartItem
from orders.models import OrderProduct

from category.models import Category
from .forms import ReviewForm
from .models import Product, ProductGallery, ReviewRating
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

def store(request, category_slug=None):
    category = None
    products = None

    if category_slug is not None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True).order_by('-id')
        paginator = Paginator(products, 12)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        products_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('-id')
        paginator = Paginator(products, 12)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        products_count = products.count()

    context = {
        'products': paged_products,
        'products_count': products_count,
    }
    return render(request, 'store/store.html', context)


def product_detail(request: HttpRequest, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    
    try:
        ordered_product = OrderProduct.objects.filter(
            user=request.user,
            product_id=single_product.id
            ).exists()
    except (OrderProduct.DoesNotExist, TypeError):
        ordered_product = None
    
    
    # Get the reviews
    reviews = ReviewRating.objects.filter(
        product_id=single_product.id,
        status=True
        ).order_by('-id')
    
    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'ordered_product': ordered_product,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    return render(request, 'store/product_detail.html', context)

def search(request: HttpRequest):
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        if keyword:
            products = Product.objects.order_by('-created_at').filter(
                Q(description__icontains = keyword) |
                Q(product_name__icontains = keyword)
                )
            products_count = products.count()
        else:
            return redirect('store')
    context = {
        'products': products,
        'products_count': products_count,
    }
    return render(request, 'store/store.html', context)


@login_required(login_url='login')
def submit_review(request: HttpRequest, product_id=None):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(
                user__id=request.user.id,
                product__id=product_id
                )
            form = ReviewForm(request.POST, instance=review)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
    return redirect(url)