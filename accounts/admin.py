from django.contrib import admin
from .models import Profile, CartItem, Cart
# Register your models here.

admin.site.register(Profile)
admin.site.register(Cart)
admin.site.register(CartItem)