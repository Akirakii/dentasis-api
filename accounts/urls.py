from django.urls import path
from knox import views as knox_views
from accounts import views

app_name = "accounts"
urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    # path("auth-user/", views.AuthenticatedUser.as_view(), name="auth-user"),
    path("logout/", knox_views.LogoutView.as_view(), name="logout"),
    path(
        "resend-activation/",
        views.ResendActivationCodeView.as_view(),
        name="resend-activation",
    ),
    path(
        "activate-account/",
        views.AccountActivationView.as_view(),
        name="activate-account",
    ),
    path(
        "send-recovery-code/",
        views.SendRecoveryCodeView.as_view(),
        name="send-recovery-code",
    ),
    path(
        "update-password/",
        views.UpdatePasswordView.as_view(),
        name="update-password",
    ),
]
