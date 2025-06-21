from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("activate/<token>/", views.activate_account, name="activate"), # Changed
    path("login/", views.AccountLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("resend-verification/", views.resend_verification_email_view, name="resend_verification_email"),
]
