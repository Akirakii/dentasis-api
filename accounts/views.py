from django.contrib.auth import get_user_model, logout, login
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from accounts import utils
from accounts.models import UserActivationCode
from accounts.serializers import (
    AcountActivationSerializer,
    ResendActivationCodeSerializer,
    UserSerializer,
    LoginSerializer,
)

User = get_user_model()


class RegisterView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def post(self, request):
        """
        Register a new User.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
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
        user = serializer.validated_data["user"]
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
                user = User.objects.get(email=email)
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
        Refresh the activation code and resends it to the user via email
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            activation_code = serializer.validated_data["activation_code"]

            try:
                user = User.objects.get(email=email)
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
                user_activation_code = UserActivationCode.objects.get(user=user.id)
            except UserActivationCode.DoesNotExist as no_activation_code:
                return Response(
                    {"message": "Activation code is invalid"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if user_activation_code.activation_code != activation_code:
                return Response(
                    {"message": "Activation code is invalid"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.is_active = True
            user.save()
            return Response(
                {"message": "Account successfully activated"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
