from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.AccountSignUpView.as_view(), name="signup"),
    path("activate/<str:token>/", views.ActivateAccountView.as_view(), name="activate"),
    path("login/", views.AccountLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("resend-verification/", views.ResendVerificationEmailView.as_view(), name="resend_verification_email"),
]
