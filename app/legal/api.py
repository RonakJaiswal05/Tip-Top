import json
import re
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from core.models import SiteSettings
from leads import spam

from .models import ConsentRecord

ID = re.compile(r"^[A-Za-z0-9-]{4,40}$")


@require_POST
def consent(request):
    """Consent log (A8): proof ID, notice version, choices and time. No IP address is stored."""
    if spam.rate_limited(request, "consent", 30, 600):
        return JsonResponse({"error": "rate"}, status=429)
    try:
        data = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "json"}, status=400)
    if not isinstance(data, dict) or not ID.match(str(data.get("id", ""))):
        return JsonResponse({"error": "id"}, status=400)
    choices = data.get("choices") or {}
    action = data.get("action") if data.get("action") in {"accept", "reject", "save"} else "save"
    try:
        decided = datetime.fromisoformat(str(data.get("ts", "")).replace("Z", "+00:00"))
    except ValueError:
        decided = None
    cats = SiteSettings.load().consent_categories
    ConsentRecord.objects.create(
        proof_id=data["id"], version=int(data.get("v") or 0) if str(data.get("v", "")).isdigit() else 0, action=action,
        stats=bool(choices.get("stats")) and "stats" in cats, marketing=bool(choices.get("marketing")) and "marketing" in cats,
        language="en" if data.get("lang") == "en" else "de", decided_at=decided,
    )
    return JsonResponse({"ok": True})
