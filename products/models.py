from django.db import models
from base.models import BaseModel
from django.utils.text import slugify


# Create your models here.

class ProductCategory(BaseModel):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories')
    slug = models.SlugField(unique=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(ProductCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class ColorVariant(BaseModel):
    color_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.color_name


class SizeVariant(BaseModel):
    size_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.size_name


class Product(BaseModel):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ProductCategory, related_name='products', on_delete=models.CASCADE)
    description = models.TextField()
    price = models.IntegerField()
    slug = models.SlugField(unique=True, blank=True, null=True)
    color_variants = models.ManyToManyField(ColorVariant, blank=True)
    size_variants = models.ManyToManyField(SizeVariant, blank=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_product_price(self, size, color):
        price = [self.price]
        if size:
            price.append(SizeVariant.objects.get(size_name=size).price)
        if color:
            price.append(ColorVariant.objects.get(color_name=color).price)

        return sum(price)


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, related_name='product_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products')


class Coupon(BaseModel):
    code = models.CharField(max_length=100)
    is_expired = models.BooleanField(default=False)
    discount_price = models.IntegerField(default=100)
    min_amount = models.IntegerField(default=500)
