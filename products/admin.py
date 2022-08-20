from django.contrib import admin
from .models import Product, ProductCategory, ProductImage, ColorVariant, SizeVariant, Coupon

# Register your models here.

admin.site.register(Coupon)

@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    model = ColorVariant


@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    model = ColorVariant


class ProductImageAdmin(admin.StackedInline):
    model = ProductImage


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]


admin.site.register(ProductCategory)
admin.site.register(Product, ProductAdmin)
