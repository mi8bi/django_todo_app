from django.contrib.auth.views import LoginView
from django.urls import reverse
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
            context["error_msg"] = _("アカウントが有効化されていません。メール認証を完了してください。")
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


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_active = False  # Deactivate account until email confirmation
            user.save()
            send_verification_email(user, request)
            # It's better to redirect to a page that informs the user to check their email
            # For now, using HttpResponse as per existing code.
            messages.info(request, "確認メールを送信しました。メールを確認してアカウントを有効化してください。")
            return redirect('accounts:login') # Or a dedicated "check your email" page
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


def activate_account(request, token):
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


def resend_verification_email_view(request):
    if request.method == 'POST':
        form = forms.ResendVerificationEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                if not user.is_active:
                    send_verification_email(user, request)
                    messages.success(request, '確認メールを再送信しました。メールを確認してください。')
                else:
                    messages.info(request, 'このアカウントは既に有効化されています。ログインしてください。')
                return redirect('accounts:login')
            except User.DoesNotExist:
                messages.error(request, 'このメールアドレスに紐づくアカウントは見つかりませんでした。')
        # If form is invalid, it will be re-rendered with errors below
    else:
        form = forms.ResendVerificationEmailForm()

    return render(request, 'resend_verification_email.html', {'form': form})