"""Turn a legal page's HTML into sections with anchors and a table of contents (the prototype's renderLegal)."""
import re

from django.utils.html import escape
from django.utils.safestring import mark_safe

H2 = re.compile(r"<h2[^>]*>(.*?)</h2>", re.S | re.I)
PART = re.compile(r'<p class="lg-part">.*?</p>', re.S)


def sections(body_html: str) -> tuple[str, list[tuple[str, str]]]:
    """-> (html with <section id="lgsN"> around each h2 block, [(anchor, title)])."""
    out, toc = [], []
    pos, idx = 0, 0
    tokens = []
    for m in re.finditer(r'<h2[^>]*>.*?</h2>|<p class="lg-part">.*?</p>', body_html, re.S | re.I):
        tokens.append(m)
    if not tokens:
        return body_html, []
    out.append(body_html[: tokens[0].start()])
    open_sec = False
    for i, m in enumerate(tokens):
        end = tokens[i + 1].start() if i + 1 < len(tokens) else len(body_html)
        chunk = body_html[m.end():end]
        if open_sec:
            out.append("</section>")
            open_sec = False
        if m.group(0).lower().startswith("<h2"):
            anchor = f"lgs{idx}"
            title = H2.match(m.group(0)).group(1)
            toc.append((anchor, title))
            out.append(f'<section id="{anchor}">{m.group(0)}{chunk}')
            open_sec = True
            idx += 1
        else:
            out.append(m.group(0) + chunk)
    if open_sec:
        out.append("</section>")
    return "".join(out), toc


def render(body_html: str, toc_label: str) -> tuple[str, str]:
    body, toc = sections(body_html)
    toc_html = ""
    if len(toc) > 12:
        items = "".join(f'<li><a href="#{a}" data-lgto="{a}">{t}</a></li>' for a, t in toc)
        toc_html = f'<nav class="lg-toc" aria-label="{escape(toc_label)}"><b>{escape(toc_label)}</b><ol>{items}</ol></nav>'
    return mark_safe(toc_html), mark_safe(body)
