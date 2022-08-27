from django.urls import path
from knox import views as knox_views
from accounts import views

app_name = "accounts"
urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
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
]
