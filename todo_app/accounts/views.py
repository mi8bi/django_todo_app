from django.contrib.auth.views import LoginView
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from .forms import SignUpForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from django.views import View
from django.views.generic.edit import FormView

from . import forms

User = get_user_model()


def get_verification_serializer():
    return URLSafeTimedSerializer(
        settings.SECRET_KEY,
        salt=settings.EMAIL_VERIFICATION_SALT
    )


class AccountLoginView(LoginView):
    template_name = "login.html"
    form_class = forms.LoginForm
    redirect_authenticated_user = True

    def form_invalid(self, form):
        context = self.get_context_data()
        context["error_msg"] = _("login error msg")
        return self.render_to_response(context)

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active:
            context = self.get_context_data()
            context["error_msg"] = _("login not active")
            return self.render_to_response(context)
        return super().form_valid(form)


def send_verification_email(user, request):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account'
    serializer = get_verification_serializer()
    token = serializer.dumps(user.email)
    # reverseでURLを生成（i18n_patterns対応）
    activation_path = reverse('accounts:activate', kwargs={'token': token})
    activation_link = f"{request.scheme}://{current_site.domain}{activation_path}"

    message = render_to_string('activation_email.html', {
        'user': user,
        'activation_link': activation_link,
    })

    email = EmailMessage(mail_subject, message, to=[user.email])
    email.send()


class AccountSignUpView(FormView):
    template_name = "signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        email = form.cleaned_data["email"]
        # ユーザ名またはメールアドレスの重複チェック
        if User.objects.filter(email=email).exists():
            form.add_error("email", _("This email address is already in use."))
            return self.form_invalid(form)
        if User.objects.filter(email=email).exists():
            form.add_error("email", "このメールアドレスは既に使用されています。")
            return self.form_invalid(form)
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.is_active = False  # メール認証が完了するまで無効化
        user.save()
        send_verification_email(user, self.request)
        messages.info(self.request, "確認メールを送信しました。メールを確認してアカウントを有効化してください。")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class ActivateAccountView(View):
    def get(self, request, token):
        serializer = get_verification_serializer()
        try:
            email = serializer.loads(
                token,
                max_age=settings.EMAIL_VERIFICATION_TOKEN_MAX_AGE_SECONDS
            )
            user = User.objects.get(email=email)
            if user.is_active:
                messages.info(request, "アカウントは既に有効化されています。")
                return render(request, "activation_complete.html", {"already_active": True})
            else:
                user.is_active = True
                user.save()
                messages.success(request, "アカウントが有効化されました！ログインしてください。")
                return render(request, "activation_complete.html", {"already_active": False})
        except SignatureExpired:
            messages.error(request, "確認リンクの有効期限が切れています。新しい確認メールをリクエストしてください。")
            return redirect('accounts:resend_verification_email')
        except BadTimeSignature:
            messages.error(request, "確認リンクが無効です。")
            return redirect('accounts:signup')
        except User.DoesNotExist:
            messages.error(request, "アカウントが見つかりません。再度登録をお試しください。")
            return redirect('accounts:signup')
        except Exception:
            messages.error(request, "アカウントの有効化中にエラーが発生しました。")
            return redirect('accounts:signup')


class ResendVerificationEmailView(FormView):
    template_name = 'resend_verification_email.html'
    form_class = forms.ResendVerificationEmailForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                send_verification_email(user, self.request)
                messages.success(self.request, '確認メールを再送信しました。メールを確認してください。')
            else:
                messages.info(self.request, 'このアカウントは既に有効化されています。ログインしてください。')
            return redirect('accounts:login')
        except User.DoesNotExist:
        except User.DoesNotExist:
            form.add_error('email', _('No account was found with this email address.'))
            return self.form_invalid(form)
