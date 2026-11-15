"""Write static/test/expected_labels.json: what the calculator's repair step must show for every model."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tiptop.settings.dev")
import django  # noqa: E402

django.setup()
from catalog.services import fmt_eur, is_from, price, services_for, snapshot  # noqa: E402

snap = snapshot()
out = {}
for lang, frm, req in (("de", "ab", "Preis auf Anfrage"), ("en", "from", "Price on request")):
    exp = {}
    for m in snap["models"]:
        labels = {}
        for k in services_for(snap, m):
            if snap["rep"][k]["tiers"]:
                vals = [v for v in (price(snap, m, k, "p"), price(snap, m, k, "o")) if v is not None]
                labels[k] = f"{frm} {fmt_eur(min(vals), lang)}" if vals else req
            else:
                v = price(snap, m, k)
                labels[k] = req if v is None else (f"{frm} " if is_from(snap, m, k) else "") + fmt_eur(v, lang)
        exp[m["slug"]] = labels
    out[lang] = exp
target = Path(__file__).resolve().parents[2] / "static" / "test" / "expected_labels.json"
target.parent.mkdir(exist_ok=True)
target.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print(target, sum(len(v) for v in out["de"].values()), "labels per language")
