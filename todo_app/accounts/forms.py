from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="UserName",
        max_length=100,
        widget=forms.TextInput(
            attrs={"id": "username", "placeholder": _("login username placeholder")}
        ),
    )
    password = forms.CharField(
        label="Password",
        max_length=20,
        widget=forms.PasswordInput(
            attrs={"id": "password", "placeholder": _("login password placeholder")}
        ),
    )


class SignUpForm(forms.ModelForm):
    username = forms.CharField(
        label="UserName",
        max_length=100,
        widget=forms.TextInput(
            attrs={"id": "signup-username", "placeholder": _("signup username placeholder")}
        ),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"id": "signup-email", "placeholder": _("signup email placeholder")}
        ),
    )
    password = forms.CharField(
        label="Password",
        max_length=20,
        widget=forms.PasswordInput(
            attrs={"id": "signup-password", "placeholder": _("signup password placeholder")}
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password")


class ResendVerificationEmailForm(forms.Form):
    email = forms.EmailField(
        label=_("Email address"),
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": _("Enter your email address")})
    )
