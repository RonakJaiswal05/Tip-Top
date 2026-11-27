# 27 Nov 2026: requests from the Claude Code port (see CLAUDE.md, "Requests for the chat").
# 1. The hours list had overridden T.closed ("geschlossen"), which openStatus() needs for "Geschlossen, öffnet {d} um 10 Uhr".
#    The list now uses its own key closed_day.
rep('closed:"closed", ask_l', 'closed_day:"closed", ask_l')
rep('closed:"geschlossen", ask_l', 'closed_day:"geschlossen", ask_l')
rep('<b>${esc(t("closed"))', '<b>${esc(t("closed_day"))')
# 2. Shop card at 320-380 px and footer hours on phones: same CSS as the Django site (app/static/site/css/port-additions.css).
s = s.replace('</style>', '''/* shop card at 320-380 px: pin the column to the card width, tighten the hours box */
.shop .shop-b{grid-template-columns:minmax(0,1fr)}
@media (max-width:380px){
  .shop .shop-b{padding-left:18px;padding-right:18px}
  .shop .shop-b .srate{flex-wrap:wrap;row-gap:2px}
  .shop .shop-h{padding-left:12px;padding-right:12px;gap:8px}
  .shop .shop-h > .ico{display:none}
  .shop .hours{font-size:14px}
  .shop .hours li{gap:10px}
}
/* footer hours on phones: the time goes under the day if needed */
.fgrid .hours li{flex-wrap:wrap;column-gap:10px;row-gap:0}
@media (max-width:600px){.fgrid .hours{row-gap:10px}}
</style>''', 1)

# 3. Owner, 27 Nov 2026: "Joystick-Drift Reparatur" and "TMR-Joysticks (driftfrei)" were the same job. One repair stays:
#    tmr = "TMR-Joystick-Reparatur (driftfrei)" (js/engine.js, js/parse.js). Popular console repairs without "drift":
rep('console:["display","hdmi","drift","tmr","battery","cport","fan","drive","psu","buttons"] };',
    'console:["display","hdmi","tmr","battery","cport","fan","drive","psu","buttons"] };')

# 4. Call with the owner, 27 Nov 2026 -----------------------------------------------------------------------------
# WhatsApp button in the hero: "Schreib uns dein Problem" under "WhatsApp".
rep('<span class="hc-t"><b>WhatsApp</b><small>030 814 757 91</small></span>', '<span class="hc-t"><b>WhatsApp</b><small data-t="wa_sub"></small></span>')

# The film on phones and tablets too: a "Film ansehen" button on the hero photo opens the vertical film with sound.
# Desktop and laptop keep the muted film inside the photo frame.
rep('''function heroVideoMake() {''', '''const FILM_M = "img/tiptop-film-m.mp4?v=2";
function heroPlayBtn(f) {
  if (f.querySelector(".hero-play")) return;
  const b = document.createElement("button"); b.type = "button"; b.className = "hero-play";
  b.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z" fill="currentColor"/></svg><span>' + esc(t("film_btn")) + "</span>";
  b.addEventListener("click", () => filmOpen(b)); f.appendChild(b);
}
function filmOpen(from) {
  let box = $("filmBox");
  if (!box) {
    box = document.createElement("div"); box.id = "filmBox"; box.className = "filmbox"; box.hidden = true;
    box.setAttribute("role", "dialog"); box.setAttribute("aria-modal", "true");
    box.innerHTML = '<div class="fb-in"><button type="button" class="fb-x"></button><video controls playsinline preload="none"></video></div>';
    document.body.appendChild(box);
    box.addEventListener("click", e => { if (e.target === box) filmClose(); });
    box.querySelector(".fb-x").addEventListener("click", filmClose);
    box.addEventListener("keydown", e => { if (e.key === "Escape") { e.preventDefault(); filmClose(); } });
  }
  const v = box.querySelector("video"), x = box.querySelector(".fb-x");
  box.setAttribute("aria-label", t("film_btn")); x.textContent = t("close"); x.setAttribute("aria-label", t("close"));
  box._from = from; if (!v.src) v.src = FILM_M;
  box.hidden = false; document.documentElement.classList.add("noscroll");
  v.currentTime = 0; v.play().catch(() => {}); x.focus();
  if (HV && HV.v) HV.v.pause();
}
function filmClose() {
  const box = $("filmBox"); if (!box || box.hidden) return;
  box.querySelector("video").pause(); box.hidden = true; document.documentElement.classList.remove("noscroll");
  if (box._from && box._from.isConnected) box._from.focus();
  if (HV && HV.on && HV.seen && HV_MQ.matches) HV.v.play().catch(() => {});
}
function heroVideoMake() {''')
rep('''  if (!HV) { if (!heroVideoOk()) return; heroVideoMake(); }''', '''  if (!HV) { if (!heroVideoOk()) { heroPlayBtn(f); return; } heroVideoMake(); }''')

# Map: Google Maps loads only after a click ("Karte laden"), for this visit only.
rep('''      <div class="shops one" id="shopList"></div>''', '''      <div class="shops one" id="shopList"></div>
      <div class="smap" id="shopMap"></div>''')
rep('''  const w = t("ways");
  $("ways").innerHTML''', '''  renderMap();
  const w = t("ways");
  $("ways").innerHTML''')
rep('''const mapsUrl = sh => ''', '''function renderMap() {
  const box = $("shopMap"); if (!box) return;
  const sh = SHOPS[0];
  if (box.querySelector("iframe")) { box.querySelector("iframe").title = t("map_title"); return; }
  let on = false; try { on = sessionStorage.getItem("tt-map") === "1"; } catch (e) {}
  if (on) { mapLoad(); return; }
  box.innerHTML = `<div class="smap-ph"><div class="smap-art" aria-hidden="true"><i class="r1"></i><i class="r2"></i><i class="r3"></i><span class="smap-pin">${ic("store", 2)}</span></div>
    <div class="smap-t"><b>${esc(t("map_h"))}</b><p class="smap-a">${esc(sh.street)}, ${esc(sh.zip)}</p><p class="smap-n">${esc(t("map_p"))}</p>
    <div class="smap-acts"><button type="button" class="btn" id="mapLoad">${esc(t("map_btn"))}</button><a class="btn line" href="${mapsUrl(sh)}" target="_blank" rel="noopener">${ic("store")}${esc(t("directions"))}</a></div></div></div>`;
  $("mapLoad").onclick = () => { try { sessionStorage.setItem("tt-map", "1"); } catch (e) {} mapLoad(true); };
}
function mapLoad(focus) {
  const box = $("shopMap"), sh = SHOPS[0];
  box.innerHTML = `<iframe class="smap-f" src="https://www.google.com/maps?q=${encodeURIComponent(sh.q)}&z=16&hl=${lang}&output=embed" title="${esc(t("map_title"))}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>`;
  if (focus) box.querySelector("iframe").focus();
}
const mapsUrl = sh => ''')

rep('/* ===== Language, routing, boot ===== */', '''Object.assign(T.de, { wa_sub:"Schreib uns dein Problem", film_btn:"Film ansehen", close:"Schließen",
  map_h:"So findest du uns", map_p:"Die Karte kommt von Google Maps. Erst wenn du sie lädst, werden Daten an Google übertragen.",
  map_btn:"Karte laden", map_title:"Karte: TipTop Service 24, Beusselstraße 18, Berlin-Moabit" });
Object.assign(T.en, { wa_sub:"Message us your problem", film_btn:"Watch the film", close:"Close",
  map_h:"How to find us", map_p:"The map comes from Google Maps. Data is only sent to Google once you load it.",
  map_btn:"Load map", map_title:"Map: TipTop Service 24, Beusselstraße 18, Berlin-Moabit" });
/* ===== Language, routing, boot ===== */''')

# Privacy policy: the click-to-load map (draft, for the lawyer's review like all legal texts).
rep('''Vorher werden keine Daten an diese Anbieter übertragen.</p>`],''', '''Vorher werden keine Daten an diese Anbieter übertragen.</p>`],
  ["Karte von Google Maps (erst nach Klick)", `<p>Unter unserer Ladenkarte kannst du eine Karte von Google Maps laden (Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Irland). Sie wird erst geladen, wenn du auf „Karte laden“ klickst. Dann überträgt dein Browser Daten wie deine IP-Adresse und die aufgerufene Seite an Google, Google kann Cookies setzen, und Daten können an Google LLC in den USA übertragen werden. Rechtsgrundlage ist deine Einwilligung durch den Klick (Art. 6 Abs. 1 lit. a DSGVO, § 25 Abs. 1 TDDDG). Die Karte bleibt nur für diesen Besuch geladen; danach fragen wir wieder. Mehr dazu: https://policies.google.com/privacy</p>`],''')
rep('''No data is sent to these providers before that.</p>`],''', '''No data is sent to these providers before that.</p>`],
  ["Google Maps map (only after a click)", `<p>Below our shop card you can load a map from Google Maps (Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Ireland). It only loads when you click “Load map”. Your browser then sends data such as your IP address and the page you are on to Google, Google may set cookies, and data may be transferred to Google LLC in the USA. The legal basis is your consent by clicking (Art. 6(1)(a) GDPR, § 25(1) TDDDG). The map stays loaded for this visit only; after that we ask again. More: https://policies.google.com/privacy</p>`],''')

s = s.replace('</style>', '''/* hero: film button on phones and tablets, film dialog */
.hero-play{position:absolute;z-index:6;right:14px;bottom:14px;display:inline-flex;align-items:center;gap:8px;height:44px;padding:0 16px 0 12px;border:0;border-radius:10px;background:rgba(18,20,28,.82);color:#fff;font:inherit;font-weight:700;font-size:14.5px;cursor:pointer}
.hero-play svg{width:18px;height:18px;flex:none}
.hero-play:hover{background:var(--ink)}
.hero-play:focus-visible{outline:3px solid var(--cobalt);outline-offset:3px}
@media(max-width:599px){.hero-play{right:auto;left:10px;bottom:auto;top:10px;height:40px;font-size:13.5px}}
.filmbox{position:fixed;inset:0;z-index:200;display:grid;place-items:center;background:rgba(18,20,28,.92);padding:56px 16px 16px}
.filmbox[hidden]{display:none}
.fb-in{position:relative;width:min(100%,calc(min(86vh,960px) * 9 / 16));aspect-ratio:9/16}
.fb-in video{width:100%;height:100%;border-radius:16px;background:#000;object-fit:contain}
.fb-x{position:absolute;right:0;top:-46px;height:38px;padding:0 14px;border:0;border-radius:10px;background:#fff;color:var(--ink);font:inherit;font-weight:700;font-size:14px;cursor:pointer}
.fb-x:focus-visible{outline:3px solid var(--lemon);outline-offset:2px}
html.noscroll{overflow:hidden}
/* shop map: placeholder until the visitor loads Google Maps */
.smap{margin-top:clamp(12px,1.6vw,18px);border-radius:24px;overflow:hidden;background:var(--fog)}
.smap-f{display:block;width:100%;height:clamp(280px,32vw,400px);border:0}
.smap-ph{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);min-height:clamp(240px,26vw,320px)}
.smap-art{position:relative;overflow:hidden;background:#E6E9EE}
.smap-art i{position:absolute;background:#fff;border-radius:6px}
.smap-art .r1{left:-10%;right:-10%;top:58%;height:22px;transform:rotate(-14deg)}
.smap-art .r2{top:-10%;bottom:-10%;left:38%;width:18px;transform:rotate(9deg)}
.smap-art .r3{left:-10%;right:-10%;top:22%;height:12px;transform:rotate(6deg);opacity:.8}
.smap-pin{position:absolute;left:43%;top:44%;width:52px;height:52px;margin:-26px 0 0 -26px;border-radius:50% 50% 50% 6px;transform:rotate(-45deg);background:var(--cobalt);display:grid;place-items:center;box-shadow:0 10px 22px -10px rgba(18,20,28,.6)}
.smap-pin .ico{transform:rotate(45deg);color:#fff;font-size:24px}
.smap-t{padding:clamp(22px,3vw,40px);display:flex;flex-direction:column;justify-content:center;gap:6px}
.smap-t b{font-size:clamp(22px,2.2vw,30px);line-height:1.1;letter-spacing:-.02em}
.smap-a{font-weight:650}
.smap-n{font-size:14px;color:var(--muted);max-width:44ch}
.smap-acts{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}
.smap-acts .btn{height:50px}
.smap-acts .btn.line{background:#fff;border-color:transparent}
@media(max-width:760px){.smap-ph{grid-template-columns:minmax(0,1fr)}.smap-art{height:150px}.smap-acts{display:grid;grid-template-columns:minmax(0,1fr)}.smap-acts .btn{width:100%}}
</style>''', 1)
