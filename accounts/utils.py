import binascii
import os
from django.core.mail import send_mail
from django.conf import settings

from accounts.models import UserActivationCode


def generate_activation_code(user):
    activation_code = binascii.hexlify(os.urandom(3)).decode()
    user_activation_code = UserActivationCode(
        user=user, activation_code=activation_code
    )
    user_activation_code.save()
    return activation_code


def send_activation_mail(target_email, activation_code):
    send_mail(
        subject="Account activation",
        message=f"Your activation code is: {activation_code}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[target_email],
        fail_silently=False,
    )
