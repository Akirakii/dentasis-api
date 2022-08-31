from django.contrib.auth import password_validation, authenticate
from django.core import exceptions
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer, ValidationError

from accounts.models import User

__all__ = [
    "UserSerializer",
    "LoginSerializer",
    "ResendActivationCodeSerializer",
    "AcountActivationSerializer",
    "SendRecoveryCodeSerializer",
    "UpdatePasswordSerializer",
]


class UserSerializer(ModelSerializer):
    password2 = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "password2"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, data):
        password1 = data.get("password")
        password2 = data.get("password2")
        email = data.get("email")
        user = User(email=email, password=password1)
        errors = dict()

        try:
            password_validation.validate_password(password=password1, user=user)
        except exceptions.ValidationError as e:
            errors.setdefault("password", []).extend(list(e.messages))

        if password1 != password2:
            errors.setdefault("password", []).append("Passwords must match.")

        if errors:
            raise ValidationError(errors)

        return super(UserSerializer, self).validate(data)

    def create(self, validated_data):
        user = User(email=validated_data["email"], password=validated_data["password"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, write_only=True)
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = serializers.CharField(read_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user: User = authenticate(
                request=self.context.get("request"),
                email=email,
                password=password,
            )

            if not user:
                msg = "Unable to log in with provided credentials."
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code="authorization")

        data["user"] = user
        return data


class ResendActivationCodeSerializer(Serializer):
    email = serializers.EmailField(max_length=254)


class AcountActivationSerializer(Serializer):
    email = serializers.EmailField(max_length=254)
    activation_code = serializers.CharField(max_length=6)


class SendRecoveryCodeSerializer(Serializer):
    email = serializers.EmailField(max_length=254)


class UpdatePasswordSerializer(Serializer):
    user = serializers.ModelField(model_field=User()._meta.get_field("id"))
    password = serializers.CharField(max_length=128, write_only=True)
    password2 = serializers.CharField(max_length=128, write_only=True)
    email = serializers.EmailField(max_length=254, required=False)
    recovery_code = serializers.CharField(max_length=6, required=False)

    def validate(self, data):
        user = data.get("user")
        print(user)
        email = data.get("email", None)
        recovery_code = data.get("recovery_code", None)
        password1 = data.get("password")
        password2 = data.get("password2")
        errors = dict()

        if user is None:
            if email is None:
                errors.setdefault("email", []).append("This field is required.")
            if recovery_code is None:
                errors.setdefault("recovery_code", []).append("This field is required.")

        if password1 != password2:
            errors.setdefault("password", []).append("Passwords must match.")

        if errors:
            raise ValidationError(errors)

        return super(UpdatePasswordSerializer, self).validate(data)
