# Call with the owner on 25 Nov 2026 (Fathom "Impromptu Call") and Ronak's list of 26 Nov: new logo, search bar and
# call/WhatsApp buttons at the top, rating moved up, 030 number as phone and WhatsApp everywhere, Gmail address,
# hours one per line, review link, iPhone vs Android repair photos, joystick/TMR repairs on consoles, image prompts
# for the newest devices (iPhone 18 Pro, Galaxy S26 Ultra, PS5 Pro), desktop-only hero video slot.
import os as _os
_img = 'img/' if _os.path.isdir('img') else '../img/'

# ---------- header: new logo (mascot kept, classic upright gold lettering), number with "Bitte sofort anrufen" ----------
rep('''    <img class="logo-full" src="img/logo-tiptop.svg" alt="" width="188" height="40">
    <img class="logo-mark" src="img/logo-mark.svg" alt="" width="40" height="40">
    <b><span>Service 24</span></b>''',
    '''    <img class="logo-full" src="img/logo-tiptop.svg" alt="" width="201" height="46">
    <img class="logo-mark" src="img/logo-mark.webp" alt="" width="37" height="42">''')
rep('''  <a class="nav-tel" href="tel:+493081475791">030 814 757 91</a>''',
    '''  <a class="nav-tel" href="tel:+493081475791"><b>030 814 757 91</b><small data-t="call_now"></small></a>''')

# ---------- hero: search bar first, then call + WhatsApp, then the Google rating, then the headline ----------
rep('''        <div class="gmb-wrap" id="gmbHero"></div>
        <p class="pick-l" data-t="pick"></p>''', '''        <p class="pick-l" data-t="pick"></p>''')
rep('''        <form class="ask" id="askForm" autocomplete="off">
          <label for="askIn" class="sr" data-t="ask_l"></label>
          <input id="askIn" data-tp="ask_ph">
          <button type="button" class="mic" id="askMic" data-ta="mic"></button>
          <button type="submit" class="go" data-t="ask_go"></button>
        </form>
        <p class="ask-msg" id="askMsg" aria-live="polite"></p>
''', '')
rep('''    <div class="wrap hero-grid">
      <div>
        <h1>''', '''    <div class="wrap hero-grid">
      <div>
        <div class="hero-top">
          <form class="ask" id="askForm" autocomplete="off" role="search">
            <label for="askIn" class="sr" data-t="ask_l"></label>
            <span class="ask-ic" id="askIc" aria-hidden="true"></span>
            <input id="askIn" data-tp="ask_ph" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="askList">
            <button type="button" class="mic" id="askMic" data-ta="mic"></button>
            <button type="submit" class="go" data-t="ask_go"></button>
            <ul class="ask-list" id="askList" role="listbox" hidden></ul>
          </form>
          <p class="ask-msg" id="askMsg" aria-live="polite"></p>
          <div class="hero-cta">
            <a class="hc hc-call" href="tel:+493081475791"><span class="hc-i" id="hcCallI"></span><span class="hc-t"><b>030 814 757 91</b><small data-t="call_now"></small></span></a>
            <a class="hc hc-wa" id="hcWa" href="https://wa.me/493081475791" target="_blank" rel="noopener"><span class="hc-i" id="hcWaI"></span><span class="hc-t"><b>WhatsApp</b><small>030 814 757 91</small></span></a>
          </div>
          <div class="gmb-wrap" id="gmbHero"></div>
        </div>
        <h1>''')
rep('''  $("gmbHero").innerHTML = gmbBadge();
  watch($("heroMedia"));''', '''  $("gmbHero").innerHTML = gmbBadge();
  $("askIc").innerHTML = ic("search", 2); $("hcCallI").innerHTML = ic("call", 2); $("hcWaI").innerHTML = ic("wa", 2);
  $("hcWa").href = waLink(t("wa_general"));
  watch($("heroMedia"));
  heroVideo();''')

# Search bar: model suggestions while typing; Enter or a click opens the price calculator at the right step.
_has_vid = _os.path.exists(_img + 'hero-loop.mp4')
rep('''$("askForm").addEventListener("submit", e => { e.preventDefault(); runAsk($("askIn").value); });''',
    '''// Desktop-only background video in the hero photo frame (img/hero-loop.mp4). Phones keep the still photo.
const HERO_VIDEO = ''' + ('true' if _has_vid else 'false') + ''';
function heroVideo() {
  if (!HERO_VIDEO || !matchMedia("(min-width:900px)").matches || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const f = document.querySelector("#heroMedia .hero-frame"); if (!f || f.querySelector("video")) return;
  const v = document.createElement("video"); v.className = "hero-vid"; v.muted = true; v.loop = true; v.autoplay = true; v.playsInline = true;
  v.setAttribute("aria-hidden", "true"); v.onerror = () => v.remove(); v.src = "img/hero-loop.mp4"; f.appendChild(v);
}
function askMatches(text) {
  // Repair words ("Akku", "Display kaputt") are left out when matching model names.
  const q = norm(text).trim().split(" ").filter(w => !ASK_SKIP.has(w)).join(" "); if (q.length < 2) return [];
  const qq = q.replace(/\\s/g, ""), words = q.split(" ").filter(w => w.length > 1), r = parse(text), out = [];
  const all = CATS.flatMap(c => MODELS[c]);
  const push = m => { if (m && !out.includes(m) && out.length < 6) out.push(m); };
  push(r.m);
  for (const a of ALIASES) if (a.a.startsWith(q) || a.a.replace(/\\s/g, "").startsWith(qq)) push(a.m);
  for (const m of all) { const n = norm(m.brand + " " + m.name); if (n.includes(" " + q) || n.replace(/\\s/g, "").includes(qq)) push(m); }
  if (out.length < 6 && words.length > 1) for (const m of all) { const n = norm(m.brand + " " + m.name); if (words.every(w => n.includes(" " + w) || n.replace(/\\s/g, "").includes(w))) push(m); }
  return out.map(m => ({ m, keys:r.keys }));
}
const ASK_SKIP = new Set([...KW.flatMap(([, ws]) => ws.flatMap(w => w.split(" "))), "kaputt", "defekt", "broken", "reparatur", "repair", "wechseln", "tauschen", "austausch", "neu", "new", "mein", "meine", "my", "ist", "is", "geht", "nicht"].filter(w => !/^(pro|max|plus|mini|air|ultra|lite|fe|note|edge|fold|flip)$/.test(w)));
let ASK = { items:[], i:-1 };
function askRender() {
  const inp = $("askIn"), list = $("askList");
  ASK.items = askMatches(inp.value); ASK.i = -1;
  if (!ASK.items.length) { list.hidden = true; inp.setAttribute("aria-expanded", "false"); inp.removeAttribute("aria-activedescendant"); return; }
  list.innerHTML = ASK.items.map(({ m, keys }, i) => { const k = keys.find(x => servicesFor(m).includes(x)) || "display";
    return `<li role="option" id="askO${i}" data-i="${i}" aria-selected="false"><span class="ao-n"><small>${esc(t("cat_" + m.cat))}</small><b>${esc(fullName(m))}</b></span><span class="ao-p">${esc(svName(k, m.cat))}<b>${esc(priceLabel(m, k))}</b></span></li>`; }).join("");
  list.hidden = false; inp.setAttribute("aria-expanded", "true");
}
function askPick(i) {
  const it = ASK.items[i]; if (!it) return;
  const valid = it.keys.filter(k => k === "diagnosis" || servicesFor(it.m).includes(k));
  $("askList").hidden = true; $("askIn").setAttribute("aria-expanded", "false");
  openBuilder({ model:it.m, cat:it.m.cat, sel:valid.map(k => k === "display" ? { key:k, tier:"p" } : { key:k }) });
}
function askMove(d) {
  if ($("askList").hidden || !ASK.items.length) return;
  ASK.i = (ASK.i + d + ASK.items.length) % ASK.items.length;
  $("askList").querySelectorAll("li").forEach((li, i) => li.setAttribute("aria-selected", i === ASK.i));
  $("askIn").setAttribute("aria-activedescendant", "askO" + ASK.i);
}
$("askIn").addEventListener("input", askRender);
$("askIn").addEventListener("keydown", e => {
  if (e.key === "ArrowDown") { e.preventDefault(); askMove(1); }
  else if (e.key === "ArrowUp") { e.preventDefault(); askMove(-1); }
  else if (e.key === "Escape") { $("askList").hidden = true; $("askIn").setAttribute("aria-expanded", "false"); }
});
$("askIn").addEventListener("blur", () => setTimeout(() => { $("askList").hidden = true; $("askIn").setAttribute("aria-expanded", "false"); }, 150));
$("askList").addEventListener("mousedown", e => e.preventDefault());
$("askList").addEventListener("click", e => { const li = e.target.closest("li[data-i]"); if (li) askPick(+li.dataset.i); });
$("askForm").addEventListener("submit", e => { e.preventDefault(); if (ASK.i >= 0 && !$("askList").hidden) askPick(ASK.i); else { $("askList").hidden = true; runAsk($("askIn").value); } });''')

# ---------- one number for calls and WhatsApp, new email, Moabit in the address, hours one per line ----------
rep('''      <a class="fmail" href="mailto:info@tiptophandyreparatur.de">info@tiptophandyreparatur.de</a><br>
      <a class="fmail" href="https://wa.me/4917672746296" target="_blank" rel="noopener">WhatsApp +49 176 72746296</a>''',
    '''      <span class="fcall" data-t="call_now"></span><br>
      <a class="fmail" href="mailto:tiptophandyreparatur@gmail.com">tiptophandyreparatur@gmail.com</a><br>
      <a class="fmail" href="https://wa.me/493081475791" target="_blank" rel="noopener">WhatsApp 030 814 757 91</a>''')
rep('''  <footer>
    <div class="wrap">
      <a class="ftel"''', '''  <footer>
    <div class="wrap">
      <img class="flogo" src="img/logo-tiptop.svg" alt="TipTop" width="245" height="56" loading="lazy"><br>
      <a class="ftel"''')
rep('''<div><h4>Berlin-Moabit</h4><p>Beusselstraße 18<br>10553 Berlin</p></div>''', '''<div><h4>Berlin-Moabit</h4><p>Beusselstraße 18<br>10553 Berlin-Moabit</p></div>''')
rep('''<div><h4 data-t="f_hours_h"></h4><p data-t="f_hours"></p></div>''', '''<div><h4 data-t="f_hours_h"></h4><div id="fHours"></div></div>''')
rep('''zip:"10553 Berlin", q:"TipTop Service 24''', '''zip:"10553 Berlin-Moabit", q:"TipTop Service 24''')
rep('''      <p class="shop-h">${ic("clock", 1.9)}<span>${esc(t("f_hours"))}</span></p>''',
    '''      <div class="shop-h">${ic("clock", 1.9)}${hoursList()}</div>
      <p class="shop-call"><a href="tel:${sh.tel}">${ic("call", 2)}${esc(t("call_now"))}</a></p>''')
rep('''function renderShops() {''', '''// Opening hours, one day per line (Sunday spelled out as closed). Same times as openStatus().
const HOURS = [["10:00", "20:00"], ["10:00", "20:00"], ["10:00", "20:00"], ["10:00", "20:00"], ["10:00", "20:00"], ["10:00", "20:00"], null];
function hoursList() {
  const d = lang === "de" ? ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"] : ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  let today = -1; try { today = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].indexOf(new Intl.DateTimeFormat("en-GB", { timeZone:"Europe/Berlin", weekday:"short" }).format(new Date())); } catch (e) {}
  return `<ul class="hours">${d.map((n, i) => `<li${i === today ? ' class="today"' : ""}><span>${n}</span><span>${HOURS[i] ? HOURS[i][0] + "–" + HOURS[i][1] + (lang === "de" ? " Uhr" : "") : `<b>${esc(t("closed"))}</b>`}</span></li>`).join("")}</ul>`;
}
function renderShops() {
  if ($("fHours")) $("fHours").innerHTML = hoursList();''')

# Google rating badges open the reviews directly.
rep('''const num1 = x =>''', '''const gmbRev = g => "https://search.google.com/local/reviews?placeid=" + g.pid;
const num1 = x =>''')
rep('''  return `<a class="gmb" href="${gmbUrl(g)}"''', '''  return `<a class="gmb" href="${gmbRev(g)}"''')
rep('''  return `<a class="srate" href="${gmbUrl(g)}"''', '''  return `<a class="srate" href="${gmbRev(g)}"''')

# ---------- repair photos: iPhone photos only for Apple, Android photos for every other phone ----------
_and = [("display", "and-display"), ("battery", "and-battery"), ("port", "and-port"), ("back", "and-back"), ("camera", "and-camera"), ("water", "and-water")]
_have_and = sorted(i for _, i in _and if _os.path.exists(_img + i + '.jpg'))
rep('''function repImg(cat, k) {
  if (!cat || cat === "phone") return REP_IMG[k] || null;''',
    '''// Phones: the iPhone photos (rep-*) only for Apple models; Samsung, Xiaomi and all other phones get the Android set (and-*).
const REP_AND = { ''' + ", ".join(f'{k}:"{i}"' for k, i in _and) + ''' };
IMG_HAVE_AND.forEach(x => IMG_HAVE.add(x));
function repImg(cat, k, brand) {
  if (!cat || cat === "phone") { if (brand === "Apple" || brand === undefined) return REP_IMG[k] || null; const id = REP_AND[k]; return id && IMG_HAVE.has(id) ? id : null; }''')
rep('''const IMG_HAVE = new Set(''', '''const IMG_HAVE_AND = ''' + repr(_have_and).replace("'", '"') + ''';
const IMG_HAVE = new Set(''')
rep('''<span class="rc-m">${repImg(m.cat, k) ? ph(repImg(m.cat, k)) : `<span class="icon-tile">''',
    '''<span class="rc-m">${repImg(m.cat, k, m.brand) ? ph(repImg(m.cat, k, m.brand)) : `<span class="icon-tile">''')
rep('''  const ri = k => repImg(B.cat, k);''', '''  const ri = k => repImg(B.cat, k, B.model ? B.model.brand : "");''')

# ---------- image list: newest devices ----------
rep('''p:"Same set-up as the smartphone image: a plain white generic game controller and a compact generic console box that resembles no real brand, side by side. Square 1:1." + PAPER("tangerine orange (#FF6A2C)") },''',
    '''p:"Same set-up as the smartphone image: a white PlayStation 5 Pro console (slim white body with the black band across the middle) lying flat, a white DualSense controller beside it, both seen from directly above. Square 1:1." + PAPER("tangerine orange (#FF6A2C)") },''')
_IP = "the newest iPhone 18 Pro Max (aluminium unibody, flat edges, very thin even bezels, small pill-shaped Dynamic Island; on the back a full-width camera plateau across the top with three large lenses)"
for old, new in [
  ('p:"A smartphone with a badly shattered screen on a blue anti-static mat next to a new replacement screen in its clear protective film with a coloured pull tab, a pink opening pick and a blue suction cup. Macro lens. Portrait 2:3." + SHOT },',
   f'p:"{_IP[0].upper() + _IP[1:]} in burgundy lies face up on a blue anti-static mat, its screen badly shattered, next to a new replacement screen in its clear protective film with a coloured pull tab, a pink opening pick and a blue suction cup. Macro lens. Portrait 2:3." + SHOT }},'),
  ('p:"An opened smartphone on a blue anti-static mat, gloved fingers (blue nitrile) lifting out the old battery by its adhesive pull tabs, a new battery beside it. Macro lens. Portrait 2:3." + SHOT },',
   f'p:"An opened iPhone 18 Pro in glacier light blue on a blue anti-static mat, screen lifted away, gloved fingers (blue nitrile) lifting out the old battery by its adhesive pull tabs, a new battery beside it. Macro lens. Portrait 2:3." + SHOT }},'),
  ('p:"Extreme close-up of the bottom edge of a smartphone on a blue anti-static mat, a gloved hand cleaning the USB-C port with a small anti-static brush with an orange handle. Macro lens. Portrait 2:3." + SHOT },',
   f'p:"Extreme close-up of the bottom edge of an iPhone 18 Pro in silver aluminium on a blue anti-static mat, speaker grilles either side of the USB-C port, a gloved hand cleaning the port with a small anti-static brush with an orange handle. Macro lens. Portrait 2:3." + SHOT }},'),
  ('p:"A smartphone face down on a blue anti-static mat showing a heavily cracked glass back with a camera bump (no logo), next to a yellow opening pick and a small heat pad. Macro lens. Portrait 2:3." + SHOT },',
   f'p:"An iPhone 18 Pro in deep blue-black face down on a blue anti-static mat: full-width aluminium camera plateau with three lenses across the top, the glass panel below it badly cracked (no logo), next to a yellow opening pick and a small heat pad. Macro lens. Portrait 2:3." + SHOT }},'),
  ('p:"Shot from directly above: a generic smartphone lies flat and upright in the centre of a light grey desk mat with space left and right, screen on with a bright abstract wallpaper of soft blue, pink and orange shapes, glass badly shattered from the lower left corner. Three opening picks (pink, orange, green) to the right. Landscape 3:2." + SHOT },',
   f'p:"Shot from directly above: {_IP} in burgundy lies flat and upright in the centre of a light grey desk mat with space left and right, screen on with a bright abstract wallpaper of soft blue, pink and orange shapes, glass badly shattered from the lower left corner. Three opening picks (pink, orange, green) to the right. Landscape 3:2." + SHOT }},'),
  ('p:"Shot from directly above: used devices on overlapping sheets of solid coloured paper (cobalt blue, bubblegum pink, jade green, tangerine orange, lemon yellow): two generic smartphones (one in a scuffed clear case), a generic tablet, a plain white game controller and a small white earbuds case. Hard direct sunlight with crisp short shadows. Portrait 2:3." + SHOT },',
   'p:"Shot from directly above: four of the newest devices with plenty of space between them on overlapping sheets of solid coloured paper (cobalt blue, bubblegum pink, jade green, lemon yellow): an iPhone 18 Pro in burgundy showing its full-width camera plateau, a silver iPad Pro, a silver MacBook Air half open, and a white PlayStation 5 DualSense controller. All like new. Hard direct sunlight with crisp short shadows. Portrait 2:3." + SHOT },'),
]:
    rep(old, new)
_ANDP = "a Samsung Galaxy S26 Ultra (flat titanium frame, slightly rounded corners, flat screen with a small centred punch-hole camera; on the back separate round camera lenses in a vertical row at the top left)"
_items = [
  ("and-display", "Display", f"{_ANDP[0].upper() + _ANDP[1:]} in titanium black lies face up on a blue anti-static mat, its screen badly shattered, next to a new replacement OLED screen in clear protective film with a coloured pull tab, a pink opening pick and a blue suction cup."),
  ("and-battery", "Battery", f"An opened {_ANDP[2:]} on a blue anti-static mat with the back glass removed, gloved fingers (blue nitrile) lifting out the rectangular battery by its pull tab, a new battery beside it."),
  ("and-port", "Charging port", f"Extreme close-up of the bottom edge of {_ANDP} on a blue anti-static mat, the S Pen slot next to the USB-C port, a gloved hand cleaning the port with a small anti-static brush with an orange handle."),
  ("and-back", "Back glass", f"{_ANDP[0].upper() + _ANDP[1:]} in titanium grey face down on a blue anti-static mat, its back glass badly cracked, the round camera lenses visible at the top left, a yellow opening pick and a small heat pad beside it."),
  ("and-camera", "Camera", f"The rear camera module of {_ANDP} held in fine tweezers above the opened phone on a blue anti-static mat, one lens cover glass cracked."),
  ("and-water", "Water damage", f"A wet, opened {_ANDP[2:]} on a blue anti-static mat, water droplets on the frame, its logic board in a small ultrasonic cleaner basket beside it, a plain unlabeled bottle of isopropyl alcohol and a soft brush."),
]
rep('''p:"A handheld games console with a cracked screen on the mat''', '''p:"A handheld games console with a cracked screen on the mat''')  # anchor check only
_last = s.rindex('\n];', 0, s.index('IMGS.forEach'))
s = s[:_last] + ",\n" + ",\n".join(f'''  {{ id:"{i}", short:"Android: {n.lower()}", name:"Repair Android: {n.lower()}", ratio:"2:3", px:"1024×1536", where:"Repair cards (Samsung and other Android phones)", attach:"img/rep-{ {'Display':'display','Battery':'battery','Charging port':'port','Back glass':'back','Camera':'camera','Water damage':'water'}[n] }.jpg (style reference)",
    p:"{p} Macro lens. Portrait 2:3." + SHOT }}''' for i, n, p in _items) + s[_last:]

# Consoles: joystick drift and TMR sticks also on home consoles and handhelds (CON in js/engine.js).

# ---------- strings ----------
rep('/* ===== Language, routing, boot ===== */', '''Object.assign(T.en, { call_now:"Call us right away", closed:"closed", ask_l:"Search your model or describe the problem",
  ask_ph:"Search model or problem, e.g. iPhone 15 screen", ask_go:"Search" });
Object.assign(T.de, { call_now:"Bitte sofort anrufen", closed:"geschlossen", ask_l:"Modell suchen oder Problem beschreiben",
  ask_ph:"Modell oder Problem suchen, z. B. iPhone 15 Display", ask_go:"Suchen" });
/* ===== Language, routing, boot ===== */''')
rep('<link rel="icon" href="img/logo-mark-180.png">', '<link rel="icon" type="image/png" href="img/logo-mark-180.png">')
s = s.replace('</style>', open('nov26.css', encoding='utf-8').read() + '\n</style>', 1)
