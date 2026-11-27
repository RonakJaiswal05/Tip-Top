"""Password reset by email for staff (A1, owner's wish of 27 Nov 2026), with a rate limit per IP address so the
form can't be used to flood an inbox. Over the limit it answers like a success and sends nothing (no hint whether an
account exists)."""
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import reverse

from leads import spam

RESET_LIMIT, RESET_WINDOW = 5, 3600


class PasswordResetView(auth_views.PasswordResetView):
    def post(self, request, *args, **kwargs):
        if spam.rate_limited(request, "pwreset", RESET_LIMIT, RESET_WINDOW):
            return redirect(reverse("password_reset_done"))
        return super().post(request, *args, **kwargs)
