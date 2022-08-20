from django.urls import path
from .views import signup, login_page, activate_email, logout_view, cart_view, cart_item_delete, coupon_remove, success, \
    invoice

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login_page, name='login'),
    path('logout/', logout_view, name='logout'),
    path('cart/', cart_view, name='cart'),
    path('cart/<uid>/remove/', cart_item_delete, name='cart_remove'),
    path('coupon/<uid>/remove/', coupon_remove, name='coupon_remove'),
    path('activate/<email_token>/', activate_email, name='activate_email'),
    path('success/', success, name='success'),
    path('invoice/', invoice, name='invoice'),
]