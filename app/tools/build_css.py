"""Build static/site/css/site.css from the prototype's CSS (the approved design) plus the Django additions.

    python tools/build_css.py      (from app/)

Run it again after the prototype changes. The prototype CSS is taken verbatim from prototype/index.html with these
adjustments for the live site: font URLs relative to the CSS file, image selectors that also match <picture>, footer
headings as h3 (heading order), and the design-time image prompt drawer removed. Site-only rules live in
static/site/css/port-additions.css.
"""
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
html = (APP.parent / "prototype" / "index.html").read_text(encoding="utf-8")
css = re.search(r"<style>\n(.*?)\n</style>", html, re.S).group(1)


def must(old, new, text, count=None):
    if old not in text:
        raise SystemExit(f"build_css: expected text not found: {old[:80]!r}")
    return text.replace(old, new) if count is None else text.replace(old, new, count)


css = must("url(fonts/", "url(../fonts/", css)
css = css.replace(".ph > img", ".ph img")
css = must(".fgrid h4{", ".fgrid h3{font-stretch:100%;letter-spacing:0;", css)
start = css.index("/* ---------- image prompt drawer ---------- */")
end = css.index("/* ---------- request form page ---------- */")
css = css[:start] + css[end:]
css = re.sub(r"\.imgbtn\{[^}]*\}\n\.imgbtn i\{[^}]*\}\n", "", css)
css = css.replace("html.cc-open .fab,html.cc-open .imgbtn{", "html.cc-open .fab{").replace(",.imgbtn{display:none!important}", "{display:none!important}")
css = css.replace("url(img/", "url(../img/")
if "imgbtn" in css or "dpanel" in css:
    raise SystemExit("build_css: image prompt drawer rules left over")
extra = (APP / "static" / "site" / "css" / "port-additions.css").read_text(encoding="utf-8")
(APP / "static" / "site" / "css" / "site.css").write_text(css + "\n" + extra, encoding="utf-8", newline="\n")
print("site.css", len(css) + len(extra), "bytes")
