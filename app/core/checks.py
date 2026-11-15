from django.conf import settings
from django.core.checks import Error, Warning, register


@register(deploy=True)
def email_backend(app_configs, **kwargs):
    """Withdrawal confirmations must really be sent in production (§ 356a BGB)."""
    if getattr(settings, "ENVIRONMENT", "") == "production" and "console" in settings.EMAIL_BACKEND:
        return [Error("Production sends email to the console. Set BREVO_API_KEY (or EMAIL_BACKEND/EMAIL_HOST).", id="tiptop.E001")]
    if getattr(settings, "ENVIRONMENT", "") == "production" and not settings.GOOGLE_PLACES_API_KEY:
        return [Warning("GOOGLE_PLACES_API_KEY is not set: the Google ratings keep the 15 Nov 2026 snapshot.", id="tiptop.W001")]
    return []
