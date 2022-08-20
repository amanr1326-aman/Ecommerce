import razorpay
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, HttpResponseRedirect, redirect, HttpResponse
from django.contrib import messages
from secrets import compare_digest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.generic import DeleteView

from base.email import send_order_detail_email
from base.helper import save_pdf
from products.models import Coupon
from .models import Profile, Cart, CartItem


def logout_view(request):
    logout(request)
    return redirect('/')


def invoice(request):
    return render(request, 'pdfs/invoice.html')


# Create your views here.
def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
            messages.error(request, "Please fill all fields")
            return HttpResponseRedirect(request.path_info)
        user = User.objects.filter(username=email)
        if not user.exists():
            messages.warning(request, "Account not found.")
            return HttpResponseRedirect(request.path_info)
        if not user[0].profile.is_email_verified:
            messages.warning(request, "Please verify your email.")
            return HttpResponseRedirect(request.path_info)
        user_obj = authenticate(username=email, password=password)
        if user_obj:
            login(request, user_obj)
            return redirect('/')
        messages.error(request, 'Incorrect credentials', 'danger')
        return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/login.html')


def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        re_password = request.POST.get('repassword')
        if not first_name or not last_name or not email or not password or not re_password:
            messages.error(request, "Please fill all fields")
            return HttpResponseRedirect(request.path_info)

        if not compare_digest(password, re_password):
            messages.error(request, "Password doesn't match")
            return HttpResponseRedirect(request.path_info)
        user = User.objects.filter(username=email)
        if user:
            messages.warning(request, "Email already taken by some user.")
            return HttpResponseRedirect(request.path_info)
        user = User(username=email, first_name=first_name, last_name=last_name, email=email)
        user.set_password(password)
        user.save()
        messages.success(request, 'An email is sent to you mail id.')
        return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/signup.html')


def cart_view(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to continue")
        return redirect('login')
    cart_obj = Cart.objects.filter(user=request.user, is_paid=False)
    if not cart_obj:
        return render(request, 'accounts/cart.html', {'cart': False, 'payment': False})
    cart = cart_obj[0]
    if not cart.cart_items.exists():
        return render(request, 'accounts/cart.html', {'cart': False, 'payment': False})
    if request.method == 'POST':
        if cart.coupon:
            messages.warning(request, "Coupon already exist.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        coupon = request.POST.get('coupon')
        coupon_objs = Coupon.objects.filter(code=coupon)
        if not coupon_objs.exists():
            messages.warning(request, "Invalid Coupon")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            coupon_obj = coupon_objs[0]
            if coupon_obj.is_expired:
                messages.warning(request, "Expired Coupon")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            if coupon_obj.min_amount > cart.get_cart_total():
                messages.warning(request, f'Minimum required cart amount is {coupon_obj.min_amount}')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            cart.coupon = coupon_obj
            cart.save()
            messages.info(request, "Coupon applied successfully")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({'amount': cart.get_cart_total() * 100, 'currency': 'INR', 'payment_capture': 1})
    cart.razorpay_order_id = payment.get('id')
    cart.save()
    return render(request, 'accounts/cart.html', {'cart': cart, 'payment': payment})


def cart_item_delete(request, uid):
    cart_item = CartItem.objects.get(pk=uid)
    if request.user == cart_item.cart.user:
        cart_item.delete()
        if cart_item.cart.coupon:
            cart = cart_item.cart
            if cart.get_cart_total() < cart.coupon.min_amount:
                cart.coupon = None
                cart.save()
        messages.info(request, "Item removed from the cart successfully.")
    else:
        messages.info(request, "You are not allowed to remove cart item.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def coupon_remove(request, uid):
    cart = Cart.objects.get(uid=uid)
    if request.user == cart.user:
        cart.coupon = None
        cart.save()
        messages.info(request, "Coupon removed.")
    else:
        messages.warning(request, "You are not allowed to remove coupon.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def success(request):
    order_id = request.GET.get('razorpay_order_id')
    razorpay_payment_id = request.GET.get('razorpay_payment_id')
    razorpay_payment_signature = request.GET.get('razorpay_signature')
    cart = Cart.objects.get(razorpay_order_id=order_id)
    cart.razorpay_payment_id = razorpay_payment_id
    cart.razorpay_payment_signature = razorpay_payment_signature
    file_name, response = save_pdf({'object': cart})
    if response:
        cart.invoice = 'pdfs/' + file_name
    cart.is_paid = True
    cart.save()
    send_order_detail_email(cart)
    return render(request, 'accounts/order.html', {'order': cart.razorpay_order_id})


def activate_email(request, email_token):
    try:
        profile = Profile.objects.get(email_token=email_token)
        profile.is_email_verified = True
        profile.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse('Invalid Token')
