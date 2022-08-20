from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from accounts.models import Cart, CartItem
from .models import Product, SizeVariant, ColorVariant


def get_products(request, slug):
    # try:
    product = Product.objects.get(slug=slug)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to continue')
            return redirect('login')
        cart_obj = Cart.objects.filter(user=request.user, is_paid=False)
        size = request.GET.get('size')
        color_variant = None
        size_variant = None
        if size:
            size_variant = SizeVariant.objects.get(size_name=size)
        color = request.GET.get('color')
        if color:
            color_variant = ColorVariant.objects.get(color_name=color)
        if not cart_obj:
            cart = Cart(user=request.user)
            cart.save()
        else:
            cart = cart_obj[0]
        cart_item = CartItem(cart=cart, product=product, color_variant=color_variant, size_variant=size_variant)
        cart_item.save()
        if request.POST.get('addproduct'):
            messages.success(request, 'Product added to cart successfully')
        if request.POST.get('buynow'):
            return redirect('cart')
    context = {
        'product': product
    }
    if request.GET.get('size') or request.GET.get('color'):
        size = request.GET.get('size')
        if size:
            context['selected_size'] = size
        color = request.GET.get('color')
        if color:
            context['selected_color'] = color
        price = product.get_product_price(request.GET.get('size'), request.GET.get('color'))
        context['updated_price'] = price
    return render(request, 'products/product.html', context)
    # except Exception as e:
    #     print(e)
