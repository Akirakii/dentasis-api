import binascii
import hashlib
import os

from django.conf import settings
from django.core.mail import send_mail

from accounts.models import UserActivationCode, UserRecoveryCode


__all__ = [
    "generate_activation_code",
    "send_activation_mail",
    "generate_recovery_code",
    "send_recovery_account_mail",
]


def generate_activation_code(user):
    activation_code = binascii.hexlify(os.urandom(3)).decode()
    hashed_activation_code = hashlib.sha256(activation_code.encode("utf-8")).hexdigest()
    user_activation_code = UserActivationCode(
        user=user, activation_code=hashed_activation_code
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


def generate_recovery_code(user):
    recovery_code = binascii.hexlify(os.urandom(3)).decode()
    hashed_recovery_code = hashlib.sha256(recovery_code.encode("utf-8")).hexdigest()
    user_recovery_code = UserRecoveryCode(user=user, recovery_code=hashed_recovery_code)
    user_recovery_code.save()
    return recovery_code


def send_recovery_account_mail(target_email, recovery_coe):
    send_mail(
        subject="Account recovery",
        message=f"Your recovery code is: {recovery_coe}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[target_email],
        fail_silently=False,
    )
