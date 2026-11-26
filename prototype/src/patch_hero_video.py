# 26 Nov 2026 (night): the TipTop film plays in the hero photo frame on desktop and laptop only (wide screen with a mouse
# or trackpad). Muted autoplay with a "Ton an" button, loaded after the page, paused when scrolled away.
# Phones and tablets keep the still photo. The separate 16:9 film section is dropped.
_has_hero = _os.path.exists(_img + 'hero-loop.mp4')
i0 = s.index('function heroVideo() {')
i1 = s.index('\n}\n', i0) + 3
s = s[:i0] + '''const HV_MQ = matchMedia("(min-width:901px) and (hover:hover) and (pointer:fine)");
let HV = null, HV_FAIL = false;
const SND_OFF = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 5 6 9H3v6h3l5 4z"/><path d="m22 9-6 6M16 9l6 6"/></svg>';
const SND_ON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 5 6 9H3v6h3l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M18.8 5.2a9.5 9.5 0 0 1 0 13.6"/></svg>';
function heroVideoOk() {
  return HERO_VIDEO && !HV_FAIL && HV_MQ.matches && !matchMedia("(prefers-reduced-motion: reduce)").matches &&
    !(navigator.connection && navigator.connection.saveData);
}
function heroVideo() {
  const f = document.querySelector("#heroMedia .hero-frame"); if (!f) return;
  if (!HV) { if (!heroVideoOk()) return; heroVideoMake(); }
  $("heroMedia").classList.add("has-vid");
  f.appendChild(HV.v); f.appendChild(HV.b); heroSndLabel();
  if (HV.on && HV.seen && HV_MQ.matches) HV.v.play().catch(() => {});
}
function heroVideoMake() {
  const v = document.createElement("video");
  v.className = "hero-vid"; v.muted = true; v.loop = true; v.playsInline = true; v.preload = "none";
  v.setAttribute("aria-hidden", "true"); v.setAttribute("disablepictureinpicture", ""); v.setAttribute("tabindex", "-1");
  const b = document.createElement("button"); b.type = "button"; b.className = "hero-snd";
  HV = { v, b, on: false, seen: true };
  v.addEventListener("playing", () => v.classList.add("on"));
  v.addEventListener("error", () => { HV_FAIL = true; v.remove(); b.remove(); $("heroMedia").classList.remove("has-vid"); HV = null; });
  b.addEventListener("click", () => { v.muted = !v.muted; if (!v.muted) v.play().catch(() => {}); heroSndLabel(); });
  const start = () => { if (!HV) return; v.src = "img/hero-loop.mp4"; HV.on = true; if (HV.seen && HV_MQ.matches) v.play().catch(() => {}); };
  if (document.readyState === "complete") setTimeout(start, 400); else addEventListener("load", () => setTimeout(start, 400), { once: true });
  if ("IntersectionObserver" in window) new IntersectionObserver(es => {
    if (!HV) return; HV.seen = es[0].isIntersecting; if (!HV.on) return;
    if (HV.seen && HV_MQ.matches) HV.v.play().catch(() => {}); else HV.v.pause();
  }, { threshold: .15 }).observe($("heroMedia"));
  HV_MQ.addEventListener("change", e => {
    if (!HV) return;
    if (e.matches) { if (HV.on && HV.seen) HV.v.play().catch(() => {}); } else { HV.v.pause(); HV.v.muted = true; heroSndLabel(); }
  });
}
function heroSndLabel() {
  if (!HV) return; const on = !HV.v.muted, l = t(on ? "snd_off" : "snd_on");
  HV.b.setAttribute("aria-pressed", String(on)); HV.b.setAttribute("aria-label", l);
  HV.b.innerHTML = (on ? SND_ON : SND_OFF) + `<span>${esc(l)}</span>`;
}
''' + s[i1:]
s = s.replace('const HERO_VIDEO = false;', 'const HERO_VIDEO = ' + ('true' if _has_hero else 'false') + ';', 1)
rep('/* ===== Language, routing, boot ===== */', '''Object.assign(T.de, { snd_on:"Ton an", snd_off:"Ton aus" });
Object.assign(T.en, { snd_on:"Sound on", snd_off:"Sound off" });
/* ===== Language, routing, boot ===== */''')
s = s.replace('</style>', '''.hero-frame .hero-vid{opacity:0;transition:opacity .7s var(--ease);background:transparent}
.hero-frame .hero-vid.on{opacity:1}
.hero-snd{position:absolute;z-index:6;right:16px;bottom:16px;display:inline-flex;align-items:center;gap:8px;height:42px;padding:0 15px 0 12px;border:0;border-radius:10px;background:rgba(18,20,28,.8);color:#fff;font:inherit;font-weight:650;font-size:14px;cursor:pointer;opacity:0;pointer-events:none;transition:opacity .5s,background .2s}
.hero-frame .hero-vid.on ~ .hero-snd{opacity:1;pointer-events:auto}
.hero-snd:hover{background:var(--ink)}
.hero-snd:focus-visible{outline:3px solid var(--cobalt);outline-offset:3px}
.hero-snd svg{width:19px;height:19px;flex:none}
@media (min-width:901px) and (hover:hover) and (pointer:fine){.hero-media.has-vid .stk{top:26%}}
@media (max-width:900px),(hover:none),(pointer:coarse){.hero-frame .hero-vid,.hero-snd{display:none}}
</style>''', 1)

# Client feedback 26 Nov: "Bitte anrufen" feels aggressive. Softer wording under every call button.
rep('call_now:"Bitte sofort anrufen"', 'call_now:"Ruf uns an"')
rep('call_now:"Call us right away"', 'call_now:"Give us a call"')
