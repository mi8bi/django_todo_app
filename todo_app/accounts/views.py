from django.contrib.auth.views import LoginView
from django.utils.translation import gettext_lazy as _

from django.shortcuts import render
from .forms import SignUpForm
from django.http import HttpResponse

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.utils.http import urlsafe_base64_decode
from django.contrib import messages


from . import forms


class AccountLoginView(LoginView):
    template_name = "login.html"
    form_class = forms.LoginForm
    redirect_authenticated_user = True

    def form_invalid(self, form):
        context = self.get_context_data()
        context["error_msg"] = _("login error msg")
        return self.render_to_response(context)


def send_verification_email(user, request):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account'
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = f"http://{current_site.domain}/accounts/activate/{uid}/{token}/"

    message = render_to_string('activation_email.html', {
        'user': user,
        'activation_link': activation_link,
    })

    email = EmailMessage(mail_subject, message, to=[user.email])
    email.send()


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_active = False  # 認証完了までログイン不可
            user.save()
            send_verification_email(user, request)
            return HttpResponse("確認メールを送信しました。メールを確認してください。")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


def activate_account(request, uidb64, token):
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "アカウントが有効化されました！")
            return redirect('accounts:login')
        else:
            messages.error(request, "無効なトークンです。")
            return redirect('accounts:signup')
    except (TypeError, ValueError, OverflowError, user.DoesNotExist):
        messages.error(request, "無効なリンクです。")
        return redirect('accounts:signup')