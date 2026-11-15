"""The TipTop admin: Django admin with two-factor sign-in for Owner and Manager (A1) and a dashboard (A2)."""
import base64

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django_otp import login as otp_login
from django_otp import user_has_device
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice

from .roles import user_in


def otp_required(user) -> bool:
    if not getattr(settings, "OTP_ENFORCE", True) or not user.is_authenticated:
        return False
    return user.is_superuser or user_in(user, *settings.OTP_REQUIRED_GROUPS)


def _verify(user, token: str):
    token = (token or "").replace(" ", "").strip()
    if not token:
        return None
    devices = list(TOTPDevice.objects.filter(user=user, confirmed=True)) + list(StaticDevice.objects.filter(user=user, confirmed=True))
    for d in devices:
        if d.verify_token(token):
            return d
    return None


class LoginForm(AdminAuthenticationForm):
    otp_token = forms.CharField(
        label="Code aus der Authenticator-App", required=False, max_length=12,
        widget=forms.TextInput(attrs={"autocomplete": "one-time-code", "inputmode": "numeric"}),
        help_text="Nur für Inhaber und Filialleitung. Alternativ einer der Notfall-Codes.",
    )

    def clean(self):
        cleaned = super().clean()
        user = self.get_user()
        self.otp_device = None
        if user and otp_required(user) and user_has_device(user, confirmed=True):
            self.otp_device = _verify(user, cleaned.get("otp_token"))
            if not self.otp_device:
                raise forms.ValidationError("Der Code aus der Authenticator-App fehlt oder ist falsch.", code="otp")
        return cleaned


class TipTopLoginView(LoginView):
    form_class = LoginForm
    template_name = "admin/login.html"

    def form_valid(self, form):
        user = form.get_user()
        auth_login(self.request, user)
        if form.otp_device:
            otp_login(self.request, form.otp_device)
        if otp_required(user) and not user_has_device(user, confirmed=True):
            return redirect("admin:otp_setup")
        return HttpResponseRedirect(self.get_success_url())


class TipTopAdminSite(admin.AdminSite):
    site_header = "TipTop Service 24 · Verwaltung"
    site_title = "TipTop Admin"
    index_title = "Übersicht"
    login_form = LoginForm
    index_template = "admin/tiptop_index.html"

    def has_permission(self, request):
        user = request.user
        if not (user.is_active and user.is_staff):
            return False
        if otp_required(user) and not user.is_verified():
            return False
        return True

    @method_decorator(never_cache)
    def login(self, request, extra_context=None):
        user = request.user
        if user.is_authenticated and user.is_staff and otp_required(user) and not user.is_verified() \
                and not user_has_device(user, confirmed=True):
            return redirect("admin:otp_setup")
        if request.method == "GET" and self.has_permission(request):
            return HttpResponseRedirect(reverse("admin:index", current_app=self.name))
        context = {**self.each_context(request), "title": "Anmelden", "subtitle": None, "app_path": request.get_full_path(),
                   "username": request.user.get_username(), **(extra_context or {})}
        if REDIRECT_FIELD_NAME not in request.GET and REDIRECT_FIELD_NAME not in request.POST:
            context[REDIRECT_FIELD_NAME] = reverse("admin:index", current_app=self.name)
        request.current_app = self.name
        return TipTopLoginView.as_view(extra_context=context)(request)

    def index(self, request, extra_context=None):
        from .dashboard import dashboard_context

        return super().index(request, {**dashboard_context(request), **(extra_context or {})})

    def get_urls(self):
        from .dashboard import dashboard_poll

        return [
            path("otp/setup/", self.otp_setup, name="otp_setup"),
            path("dashboard/poll/", self.admin_view(dashboard_poll), name="dashboard_poll"),
        ] + super().get_urls()

    @method_decorator(never_cache)
    def otp_setup(self, request):
        """Set up the authenticator app (TOTP) and show ten emergency codes once."""
        user = request.user
        if not (user.is_authenticated and user.is_active and user.is_staff):
            return redirect("admin:login")
        if user_has_device(user, confirmed=True) and not user.is_verified():
            return redirect("admin:login")  # adding a device needs the existing second factor first
        device = TOTPDevice.objects.filter(user=user, confirmed=False).first() or TOTPDevice.objects.create(
            user=user, name="Authenticator-App", confirmed=False
        )
        error = ""
        if request.method == "POST":
            if device.verify_token(request.POST.get("token", "").replace(" ", "")):
                device.confirmed = True
                device.save()
                TOTPDevice.objects.filter(user=user, confirmed=False).delete()
                static, _ = StaticDevice.objects.get_or_create(user=user, name="Notfall-Codes", defaults={"confirmed": True})
                static.token_set.all().delete()
                codes = [StaticToken.random_token() for _ in range(10)]
                for c in codes:
                    static.token_set.create(token=c)
                otp_login(request, device)
                return render(request, "admin/otp_codes.html", {**self.each_context(request), "codes": codes, "title": "Notfall-Codes"})
            error = "Der Code stimmt nicht. Bitte den aktuellen Code aus der App eingeben."
        import qrcode
        import qrcode.image.svg

        svg = qrcode.make(device.config_url, image_factory=qrcode.image.svg.SvgPathImage, box_size=8).to_string(encoding="unicode")
        return render(request, "admin/otp_setup.html", {
            **self.each_context(request), "title": "Zwei-Faktor-Anmeldung einrichten", "qr": svg,
            "secret": base64.b32encode(device.bin_key).decode(), "error": error,
        })
