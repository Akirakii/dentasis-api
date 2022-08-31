import hashlib

from django.contrib.auth import login, views
from django.utils import timezone
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from accounts import utils
from accounts.models import User, UserActivationCode, UserRecoveryCode
from accounts.serializers import (
    AcountActivationSerializer,
    UpdatePasswordSerializer,
    LoginSerializer,
    ResendActivationCodeSerializer,
    SendRecoveryCodeSerializer,
    UserSerializer,
)


class RegisterView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def post(self, request):
        """
        Register a new User.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user: User = serializer.save()
            try:
                activation_code = utils.generate_activation_code(user)
                utils.send_activation_mail(user.email, activation_code)
            except Exception:
                pass
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthenticatedUser(GenericAPIView):
    def get(self, request):
        """
        Retrieve the logged user
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = serializer.validated_data["user"]
        if not user.is_active:
            return Response(
                {"message": "User account is not activated"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        login(request, user)
        return super(LoginView, self).post(request, format=None)


class ResendActivationCodeView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ResendActivationCodeSerializer

    def post(self, request):
        """
        Refresh the activation code and resends it to the user via email
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]

            try:
                user: User = User.objects.get(email=email)
            except User.DoesNotExist as no_user:
                return Response(
                    {"message": "No such user"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if user.is_active:
                return Response(
                    {"message": "User account already activated"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            activation_code = utils.generate_activation_code(user)
            utils.send_activation_mail(user.email, activation_code)

            return Response(
                {"message": "Activation token successfully resend"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountActivationView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = AcountActivationSerializer

    def post(self, request):
        """
        Activates user
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            activation_code = serializer.validated_data["activation_code"]

            try:
                user: User = User.objects.get(email=email)
            except User.DoesNotExist as no_user:
                return Response(
                    {"message": "No such user"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if user.is_active:
                return Response(
                    {"message": "User account already activated"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                user_activation_code: UserActivationCode = (
                    UserActivationCode.objects.get(user=user.id)
                )
            except UserActivationCode.DoesNotExist as no_activation_code:
                return Response(
                    {"message": "Activation code is invalid"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            hashed_activation_code = hashlib.sha256(
                activation_code.encode("utf-8")
            ).hexdigest()

            if user_activation_code.activation_code != hashed_activation_code:
                return Response(
                    {"message": "Activation code is invalid"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if user_activation_code.expire_date < timezone.now():
                return Response(
                    {"message": "Activation code is expired"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.is_active = True
            user.save()
            user_activation_code.delete()

            return Response(
                {"message": "Account successfully activated"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendRecoveryCodeView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SendRecoveryCodeSerializer

    def post(self, request):
        """
        Creates or refresh the recovery code and sends it to the user via email
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]

            try:
                user: User = User.objects.get(email=email)
            except User.DoesNotExist as no_user:
                return Response(
                    {"message": "No such user"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not user.is_active:
                return Response(
                    {"message": "User account is not activated"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            recovery_code = utils.generate_recovery_code(user)
            utils.send_recovery_account_mail(user.email, recovery_code)

            return Response(
                {"message": "Recovery code successfully send"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UpdatePasswordSerializer

    def post(self, request):
        """
        Updates password
        """
        print({**request.data, "user": request.user})
        serializer = self.serializer_class(data={**request.data, "user": request.user.id})
        if serializer.is_valid():
            user: User = serializer.validated_data["user"]
            new_password = serializer.validated_data["password"]
            user_recovery_code: UserRecoveryCode = None

            if user.id is None:
                email = serializer.validated_data["email"]
                recovery_code = serializer.validated_data["recovery_code"]

                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist as no_user:
                    return Response(
                        {"message": "No such user"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                try:
                    user_recovery_code = UserRecoveryCode.objects.get(user=user.id)
                except UserRecoveryCode.DoesNotExist as no_recovery_code:
                    return Response(
                        {"message": "Recovery code is invalid"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                hashed_recovery_code = hashlib.sha256(
                    recovery_code.encode("utf-8")
                ).hexdigest()

                if user_recovery_code.recovery_code != hashed_recovery_code:
                    return Response(
                        {"message": "Recovery code is invalid"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if user_recovery_code.expire_date < timezone.now():
                    return Response(
                        {"message": "Activation code is expired"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if not user.is_active:
                return Response(
                    {"message": "User account is not activated"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(new_password)
            user.save()

            if user_recovery_code is not None:
                user_recovery_code.delete()

            return Response(
                {"message": "Password successfully updated"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
