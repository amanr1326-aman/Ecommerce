from django.core.mail import send_mail, EmailMessage
from django.conf import settings


def send_account_activation_email(email, email_token):
    subject = 'Your account need to be verified'
    email_from = settings.EMAIL_HOST_USER
    message = f'Hi, Please click on the link to activate your account http://127.0.0.1:8000/accounts/activate/{email_token}'
    send_mail(subject, message, email_from, [email])


def send_order_detail_email(cart):
    subject = 'Order placed'
    email_from = settings.EMAIL_HOST_USER
    message = f'Hi, Your order with order id - {cart.razorpay_order_id} is placed successfully  and it will be delivered in 2 - 5 business days.'
    email = EmailMessage(subject, message, email_from, [cart.user.email])
    email.attach_file(cart.invoice.path)
    email.send()
