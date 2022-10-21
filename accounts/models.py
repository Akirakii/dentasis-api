from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone

__all__ = [
    "User",
    "UserActivationCode",
    "UserRecoveryCode",
]


def one_day_hence():
    return timezone.now() + timezone.timedelta(days=1)


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        if not password:
            raise ValueError("The Password must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=254)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "accounts_user"
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class UserActivationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    activation_code = models.CharField(max_length=128)
    expire_date = models.DateTimeField(default=one_day_hence)

    class Meta:
        db_table = "accounts_user_activation_code"
        verbose_name = "codigo de activacion"
        verbose_name_plural = "codigos de activacion"


class UserRecoveryCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    recovery_code = models.CharField(max_length=128)
    expire_date = models.DateTimeField(default=one_day_hence)

    class Meta:
        db_table = "accounts_user_recovery_code"
        verbose_name = "codigo de recuperacion"
        verbose_name_plural = "codigos de recuperacion"
