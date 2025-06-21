from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("activate/<uidb64>/<token>/", views.activate_account, name="activate"),
    path("login/", views.AccountLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
