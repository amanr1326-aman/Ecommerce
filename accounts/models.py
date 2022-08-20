from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

from base.models import BaseModel
from base.email import send_account_activation_email
from products.models import Product, ColorVariant, SizeVariant, Coupon


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    email_token = models.CharField(blank=True, null=True, max_length=100)
    is_email_verified = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='profile')

    def get_cart_count(self):
        return CartItem.objects.filter(cart__is_paid=False, cart__user=self.user).count()


class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_signature = models.CharField(max_length=100, null=True, blank=True)
    invoice = models.FileField(upload_to='pdfs',blank=True, null=True)

    def get_cart_total(self):
        price = []
        for item in self.cart_items.all():
            price.append(item.get_product_price())
        if self.coupon:
            if self.coupon.min_amount < sum(price):
                price.append(-1*self.coupon.discount_price)
        return sum(price)


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.SET_NULL, null=True, blank=True)
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True, blank=True)

    def get_product_price(self):
        price = [self.product.price]
        if self.color_variant:
            price.append(self.color_variant.price)
        if self.size_variant:
            price.append(self.size_variant.price)
        return sum(price)


@receiver(post_save, sender=User)
def send_email_token(sender, instance, created, **kwargs):
    try:
        if created:
            email_token = str(uuid.uuid4())
            email = instance.email
            Profile.objects.create(user=instance, email_token=email_token)
            send_account_activation_email(email, email_token)
    except Exception as e:
        print(e)
