# Client feedback 15/16 Nov 2026 (voice notes + handwritten list). Runs last in build4.py.
# One shop only, no free pickup, 12-month guarantee, 20,000 customers, TLAMO gone, real workshop/shop photos,
# multi-select repairs, visible language switch on phones, photos with the buyback (Ankauf) request.

# ---------- copy ----------
rep('in Berlin-Moabit und Spandau. Preis in Sekunden', 'in Berlin-Moabit. Preis in Sekunden')
rep('consoles in Berlin-Moabit and Spandau. Most repairs', 'consoles in Berlin-Moabit. Most repairs')
rep('Konsolen in Berlin-Moabit und Spandau. Die meisten', 'Konsolen in Berlin-Moabit. Die meisten')
rep('facts:["Up to 24 months warranty","Premium or original parts","Free pickup within 5 km"],', 'facts:["Up to 12 months warranty","Premium or original parts","No appointment needed"],')
rep('facts:["Bis zu 24 Monate Garantie","Premium- oder Originalteile","Kostenlose Abholung im Umkreis von 5 km"],', 'facts:["Bis zu 12 Monate Garantie","Premium- oder Originalteile","Ohne Termin"],')
rep('glass_w:"Up to 24 months warranty",', 'glass_w:"Up to 12 months warranty",')
rep('glass_w:"Bis zu 24 Monate Garantie",', 'glass_w:"Bis zu 12 Monate Garantie",')
rep('"Yes. You get up to 24 months warranty on our repairs."', '"Yes. You get up to 12 months warranty on our repairs."')
rep('"Ja. Auf unsere Reparaturen bekommst du bis zu 24 Monate Garantie."', '"Ja. Auf unsere Reparaturen bekommst du bis zu 12 Monate Garantie."')
rep('vat:"Incl. VAT. Up to 24 months warranty.",', 'vat:"Incl. VAT. Up to 12 months warranty.",')
rep('vat:"Inkl. MwSt. Bis zu 24 Monate Garantie.",', 'vat:"Inkl. MwSt. Bis zu 12 Monate Garantie.",')
rep('nav_shops:"Shops",', 'nav_shops:"Shop",')
rep('nav_shops:"Filialen",', 'nav_shops:"Laden",')
rep('shops_h:"Two shops in Berlin", shops_p:"Two shops, no appointment needed. Monday to Saturday, 10:00 to 20:00.",',
    'shops_h:"Our shop in Moabit", shops_p:"Beusselstraße 18, 10553 Berlin. No appointment needed, Monday to Saturday, 10:00 to 20:00.",')
rep('shops_h:"Zwei Filialen in Berlin", shops_p:"Zwei Filialen, ohne Termin. Montag bis Samstag, 10 bis 20 Uhr.",',
    'shops_h:"Unser Laden in Moabit", shops_p:"Beusselstraße 18, 10553 Berlin. Ohne Termin, Montag bis Samstag, 10 bis 20 Uhr.",')
rep('["Free pickup","Within 5 km we collect your device and bring it back.","Book on WhatsApp"]',
    '["Ask on WhatsApp","Send us a photo of the damage and we\'ll tell you the price.","Open WhatsApp"]')
rep('["Kostenlose Abholung","Im Umkreis von 5 km holen wir dein Gerät ab und bringen es zurück.","Per WhatsApp buchen"]',
    '["Per WhatsApp fragen","Schick uns ein Foto vom Schaden, wir sagen dir den Preis.","WhatsApp öffnen"]')
rep('wa_pick:"Hello TipTop, I\'d like to book the free pickup service.",', 'wa_pick:"Hello TipTop, I have a question about a repair.",')
rep('wa_pick:"Hallo TipTop, ich möchte die kostenlose Abholung buchen.",', 'wa_pick:"Hallo TipTop, ich habe eine Frage zu einer Reparatur.",')
rep('wheres:["Walk in at Moabit","Walk in at Spandau","Free pickup (5 km)","Send it in"],', 'wheres:["Bring it to the shop","Send it in"],')
rep('wheres:["Vorbeikommen in Moabit","Vorbeikommen in Spandau","Kostenlose Abholung (5 km)","Einschicken"],', 'wheres:["Im Laden vorbeibringen","Einschicken"],')
rep('["Water damage","Corrosion cleaned off before it spreads."]', '["Water damage","Corrosion cleaned off, shorts found with the thermal camera."]')
rep('["Wasserschaden","Korrosion entfernt, bevor sie sich ausbreitet."]', '["Wasserschaden","Korrosion entfernt, Kurzschlüsse mit der Wärmebildkamera gefunden."]')
rep('wd_p:"Booked a pickup or mail-in repair online,', 'wd_p:"Booked a mail-in repair online,')
rep('wd_p:"Du hast eine Abholung oder Einsendung online,', 'wd_p:"Du hast eine Einsendung online,')
rep('gmb_n:"{n} Google reviews, {s} shop",', 'gmb_n:"{n} Google reviews",')
rep('gmb_n:"{n} Google-Bewertungen, Filiale {s}",', 'gmb_n:"{n} Google-Bewertungen",')
rep('''  const n = new Intl.NumberFormat(lang === "de" ? "de-DE" : "en-IE").format(15000);
  $("labNote").innerHTML = esc(t("lab_note")).replace("{n}", `<b data-count="15000">${n}</b>`);''',
    '''  const n = new Intl.NumberFormat(lang === "de" ? "de-DE" : "en-IE").format(20000);
  $("labNote").innerHTML = esc(t("lab_note")).replace("{n}", `<b data-count="20000">${n}</b>`);''')

# ---------- one shop ----------
rep(''',
  { id:"shop-spandau", g:"spandau", area:"Berlin-Spandau", street:"Havelstraße 8", zip:"13597 Berlin", q:"Havelstraße 8, 13597 Berlin", tel:"+493089617138", telTxt:"030 896 171 38" }''', '')
rep(''',
  spandau:{ r:4.0, n:44, pid:"ChIJk4noUUFWqEcR8pf5IuXJ-7U", q:"Tip Top Reparatur Service, Havelstraße 8, 13597 Berlin", s:"Spandau" }''', '')
rep('<div class="shops" id="shopList"></div>', '<div class="shops one" id="shopList"></div>')
rep('''        <div><h4>Berlin-Spandau</h4><p>Havelstraße 8<br>13597 Berlin</p></div>
''', '')
rep('''      <a class="fmail" href="mailto:info@tiptophandyreparatur.de">info@tiptophandyreparatur.de</a>''',
    '''      <a class="fmail" href="mailto:info@tiptophandyreparatur.de">info@tiptophandyreparatur.de</a><br>
      <a class="fmail" href="https://wa.me/4917672746296" target="_blank" rel="noopener">WhatsApp +49 176 72746296</a>''')
rep('<span>© 2026 TLAMO GmbH, TipTop Service 24</span>', '<span>© 2026 TipTop Service 24 Handy Reparatur Berlin</span>')

# ---------- real photos (workshop + shop front) ----------
rep(''',
  { id:"shop-spandau", short:"Spandau shop (real photo)", name:"Shop front: Spandau", ratio:"16:9", px:"landscape", where:"Shops", real:true, p:"Real photo of the Havelstraße 8 shop front, landscape." }''', '')
rep('{ id:"shop-moabit", short:"Moabit shop (real photo)", name:"Shop front: Moabit", ratio:"16:9", px:"landscape", where:"Shops", real:true, p:"Real photo of the Beusselstraße 18 shop front, landscape." }',
    '{ id:"shop-moabit", short:"Shop front (real photo)", name:"Shop front: Beusselstraße 18", ratio:"3:2", px:"1536×1024", where:"Shop", real:true, p:"Night photo of the Beusselstraße 18 shop front from the owner, retouched by his brother in ChatGPT. Swap for a more realistic retouch if the client prefers." }')
for k, nm in [("lab-solder", "Micro-soldering"), ("lab-ic", "IC repair"), ("lab-water", "Water damage"), ("lab-data", "Data recovery")]:
    i0 = s.index('{ id:"%s",' % k); i1 = s.index('},', i0) + 1
    s = s[:i0] + '{ id:"%s", short:"%s (real photo)", name:"Workshop: %s", ratio:"3:2", px:"real", where:"Workshop", real:true, p:"Real photo from the owner\'s workshop, cropped." }' % (k, nm, nm.lower()) + s[i1:]

# ---------- icons ----------
rep("check:'<path d=\"M5 12.5l4.5 4.5L19 7.5\"/>',",
    "check:'<path d=\"M5 12.5l4.5 4.5L19 7.5\"/>', globe:'<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M3 12h18M12 3c2.6 2.6 3.8 5.6 3.8 9s-1.2 6.4-3.8 9M12 3C9.4 5.6 8.2 8.6 8.2 12s1.2 6.4 3.8 9\"/>',")

# ---------- language switch visible on phones ----------
rep('''  <div class="lang" role="group" aria-label="Language"><button type="button" data-lang="en">EN</button><button type="button" data-lang="de">DE</button></div>
  <button type="button" class="cta" data-open-builder>''',
    '''  <div class="lang" role="group" aria-label="Language"><button type="button" data-lang="en">EN</button><button type="button" data-lang="de">DE</button></div>
  <button type="button" class="lang-sw" id="langSw"></button>
  <button type="button" class="cta" data-open-builder>''')
rep('''  document.querySelectorAll(".lang button").forEach(b => b.setAttribute("aria-pressed", b.dataset.lang === lang));''',
    '''  document.querySelectorAll(".lang button").forEach(b => b.setAttribute("aria-pressed", b.dataset.lang === lang));
  { const o = lang === "de" ? "en" : "de"; $("langSw").innerHTML = ic("globe", 1.8) + `<span lang="${o}">${o.toUpperCase()}</span>`; $("langSw").setAttribute("aria-label", o === "de" ? "Auf Deutsch anzeigen" : "Show in English"); $("langSw").lang = o; }''')
rep('''document.querySelectorAll(".lang button").forEach(b => b.addEventListener("click", () => { lang = b.dataset.lang; LS.set("tt-lang", lang); applyLang(); }));''',
    '''document.querySelectorAll(".lang button").forEach(b => b.addEventListener("click", () => { lang = b.dataset.lang; LS.set("tt-lang", lang); applyLang(); }));
$("langSw").addEventListener("click", () => { lang = lang === "de" ? "en" : "de"; LS.set("tt-lang", lang); applyLang(); $("langSw").focus(); });''')

# ---------- repairs: pick several at once ----------
rep('''      <div class="bld-body" id="bldBody" aria-live="polite"></div>''',
    '''      <div class="bld-body" id="bldBody" aria-live="polite"></div>
      <div class="bld-foot" id="bldFoot" hidden></div>''')
rep('''  const card = k => `<button type="button" class="rc" data-b="rep" data-v="${k}" data-hk="${k}">${REP_IMG[k] ? ph(REP_IMG[k]) : `<span class="icon-tile">${ic(k, 1.4)}</span>`}<b>${esc(svName(k, m.cat))}</b><small>${esc(priceLabel(m, k))}</small></button>`;''',
    '''  const on = k => B.sel.some(s => s.key === k);
  const card = k => `<button type="button" class="rc" data-b="rep" data-v="${k}" data-hk="${k}" aria-pressed="${on(k)}"><span class="rc-m">${REP_IMG[k] ? ph(REP_IMG[k]) : `<span class="icon-tile">${ic(ICON_OF[k] || k, 1.4)}</span>`}<span class="tick" aria-hidden="true">${ic("check", 2.8)}</span></span><b>${esc(svName(k, m.cat))}</b><small>${esc(priceLabel(m, k))}</small></button>`;''')
rep('''      ? `<div class="rlist">${rest.map(k => `<button type="button" data-b="rep" data-v="${k}" data-hk="${k}"><span>${esc(svName(k, m.cat))}</span><span>${esc(priceLabel(m, k))}</span></button>`).join("")}</div>''',
    '''      ? `<div class="rlist">${rest.map(k => `<button type="button" data-b="rep" data-v="${k}" data-hk="${k}" aria-pressed="${on(k)}"><span><i class="cb" aria-hidden="true">${ic("check", 2.8)}</i>${esc(svName(k, m.cat))}</span><span>${esc(priceLabel(m, k))}</span></button>`).join("")}</div>''')
rep('''  return `<h2 class="bt">${esc(t("r_title"))}</h2><p class="bs">${esc(fullName(m))}</p>
    <div class="rgrid">${top.map(card).join("")}</div>${restHtml}
    <button type="button" class="unsure" data-b="rep" data-v="diagnosis" data-hk="diagnosis">''',
    '''  return `<h2 class="bt">${esc(t("r_title"))}</h2><p class="bs">${esc(fullName(m))} · ${esc(t("r_multi"))}</p>
    <div class="rgrid">${top.map(card).join("")}</div>${restHtml}
    <button type="button" class="unsure" data-b="rep" data-v="diagnosis" data-hk="diagnosis" aria-pressed="${on("diagnosis")}">''')
rep('''function addSel(key, tier) {''', '''function renderFoot() {
  const f = $("bldFoot"), show = B.step === 3 && !B.done && !!B.model;
  f.hidden = !show; if (!show) { f.innerHTML = ""; return; }
  const n = B.sel.length, tt = n ? totalOf(B.model, B.sel) : null;
  f.innerHTML = `<span class="bf-t"><b>${esc(n ? t("r_count", { n }) : t("r_none"))}</b>${tt ? `<small>${esc(tt.text)}</small>` : ""}</span><button type="button" class="btn" data-b="next" ${n ? "" : "disabled"}>${esc(t("r_next"))}${ic("right", 2.2)}</button>`;
}
function toggleSel(key) {
  const i = B.sel.findIndex(s => s.key === key);
  if (i >= 0) B.sel.splice(i, 1); else addSel(key);
  $("bldBody").querySelectorAll(`[data-b="rep"][data-v="${key}"]`).forEach(x => x.setAttribute("aria-pressed", i < 0));
  renderFoot(); renderSide();
}
function addSel(key, tier) {''')
rep('''    case "rep": addSel(v); B.hoverKey = null; goB(4); break;''',
    '''    case "rep": if (B.step === 3) toggleSel(v); else { addSel(v); goB(4); } break;
    case "next": if (B.sel.length) { B.hoverKey = null; goB(4); } break;''')
rep('''  renderSide(); hydrate($("bldBody"));
  const tb = $("bTotal");''', '''  renderSide(); renderFoot(); hydrate($("bldBody"));
  const tb = $("bTotal");''')

# ---------- buyback: take or add photos and send them with the request ----------
rep('''          <div><span class="lab-l" data-t="f_cond"></span><div class="chips" id="sellCond"></div></div>
          <a class="btn-wa" id="sellWa" target="_blank" rel="noopener"></a>
          <p class="fine" id="sellFine"></p>''',
    '''          <div><span class="lab-l" data-t="f_cond"></span><div class="chips" id="sellCond"></div></div>
          <div class="sp" id="sellPh">
            <span class="lab-l" id="spLab"></span>
            <div class="sp-row" id="spRow"></div>
            <p class="sp-hint" id="spHint"></p>
            <input type="file" id="spCam" accept="image/*" capture="environment" hidden>
            <input type="file" id="spLib" accept="image/*" multiple hidden>
          </div>
          <div id="spSend"></div>
          <a class="btn-wa" id="sellWa" target="_blank" rel="noopener"></a>
          <p class="fine" id="sellFine"></p>''')
rep('''const SELL = { cat:"phone", cond:1 };''', '''const SELL = { cat:"phone", cond:1, photos:[], n:"", p:"", done:null };
const SP_MAX = 6;
/* Photos are shrunk in the browser (longest side 1600 px, JPEG) before sending. Live site: POST multipart to /api/ankauf/,
   the server strips EXIF/GPS, stores them privately and deletes them after 30 days if no purchase follows. */
function spShrink(file, max = 1600, q = .82) {
  return new Promise(res => {
    const url = URL.createObjectURL(file), im = new Image();
    im.onload = () => { const k = Math.min(1, max / Math.max(im.width, im.height)), c = document.createElement("canvas");
      c.width = Math.round(im.width * k); c.height = Math.round(im.height * k); c.getContext("2d").drawImage(im, 0, 0, c.width, c.height);
      URL.revokeObjectURL(url); res(c.toDataURL("image/jpeg", q)); };
    im.onerror = () => { URL.revokeObjectURL(url); res(null); };
    im.src = url;
  });
}
async function spAdd(files) {
  const room = SP_MAX - SELL.photos.length; let skipped = 0;
  for (const f of [...files].slice(0, Math.max(0, room))) { if (!/^image\\//.test(f.type) && !/\\.(heic|heif|jpe?g|png|webp)$/i.test(f.name)) { skipped++; continue; } const d = await spShrink(f); if (d) SELL.photos.push(d); else skipped++; }
  if (files.length > room) toast(t("sp_max", { n:SP_MAX })); else if (skipped) toast(t("sp_bad"));
  renderSellPhotos();
}
function renderSellPhotos() {
  $("spLab").textContent = t("sp_lab");
  const n = SELL.photos.length, full = n >= SP_MAX;
  $("spRow").innerHTML = SELL.photos.map((d, i) => `<span class="sp-th"><img src="${d}" alt="${esc(t("sp_alt", { n:i + 1 }))}"><button type="button" class="sp-rm" data-sprm="${i}" aria-label="${esc(t("sp_rm", { n:i + 1 }))}">${ic("x", 2.4)}</button></span>`).join("") +
    (full ? "" : `<button type="button" class="sp-add sp-cam" data-sp="cam">${ic("camera", 1.8)}<span>${esc(t("sp_cam"))}</span></button><button type="button" class="sp-add" data-sp="lib">${ic("img", 1.8)}<span>${esc(t(n ? "sp_more" : "sp_lib"))}</span></button>`);
  $("spHint").textContent = t("sp_hint", { n:SP_MAX });
  if (SELL.done) {
    $("spSend").innerHTML = `<div class="sp-ok"><span class="ck">${ic("check", 2.4)}</span><div><b>${esc(t("sp_done_t", { n:SELL.done }))}</b><p>${esc(t("sp_done"))}</p><p class="proto">${esc(t("proto"))}</p></div></div>`;
    $("sellPh").hidden = true; $("sellWa").hidden = true; return;
  }
  $("sellPh").hidden = false; $("sellWa").hidden = false;
  $("sellWa").classList.toggle("alt", n > 0);
  $("spSend").innerHTML = n ? `<div class="two"><div><label class="lab-l" for="spName">${esc(t("name_l"))}</label><input class="inp" id="spName" autocomplete="name" value="${esc(SELL.n)}"></div><div><label class="lab-l" for="spPhone">${esc(t("sp_phone"))}</label><input class="inp" id="spPhone" type="tel" autocomplete="tel" value="${esc(SELL.p)}"></div></div>
    <p class="err" id="spErr"></p><button type="submit" class="btn sp-go">${ic("check", 2.4)}${esc(t("sp_send", { n }))}</button>` : "";
}''')
rep('''  $("sellWa").innerHTML = ic("wa", 1.9) + `<span>${esc(t("sell_btn"))}</span>`;''',
    '''  $("sellWa").innerHTML = ic("wa", 1.9) + `<span>${esc(t(SELL.photos.length ? "sell_btn_alt" : "sell_btn"))}</span>`;
  renderSellPhotos();''')
rep('''$("sellForm").addEventListener("submit", e => e.preventDefault());''',
    '''$("sellForm").addEventListener("click", e => {
  const a = e.target.closest("[data-sp]"); if (a) { $(a.dataset.sp === "cam" ? "spCam" : "spLib").click(); return; }
  const r = e.target.closest("[data-sprm]"); if (r) { SELL.photos.splice(+r.dataset.sprm, 1); renderSell(); const nx = $("spRow").querySelector("button"); if (nx) nx.focus(); }
});
["spCam", "spLib"].forEach(id => $(id).addEventListener("change", e => { const fs = e.target.files; if (fs && fs.length) spAdd(fs).then(renderSell); e.target.value = ""; }));
$("sellForm").addEventListener("input", e => { if (e.target.id === "spName") SELL.n = e.target.value; if (e.target.id === "spPhone") SELL.p = e.target.value; });
$("sellForm").addEventListener("submit", e => {
  e.preventDefault(); if (!SELL.photos.length) return;
  const n = SELL.n.trim(), p = SELL.p.trim(), err = $("spErr");
  if (!n) { err.textContent = t("err_name"); $("spName").focus(); return; }
  if (p.replace(/\\D/g, "").length < 6) { err.textContent = t("err_phone"); $("spPhone").focus(); return; }
  const dev = (t("cat_" + SELL.cat) + " " + ($("sellModel").value.trim() || "")).trim();
  const req = { name:n, phone:p, device:dev, repair:t("sp_req", { k:t("conds")[SELL.cond] }), total:t("sp_count", { n:SELL.photos.length }), via:"sell" };
  // prototype: thumbnails in the local inbox (the live site uploads the full photos)
  Promise.all(SELL.photos.map(d => new Promise(res => { const im = new Image(); im.onload = () => { const k = 240 / Math.max(im.width, im.height), c = document.createElement("canvas"); c.width = Math.round(im.width * k); c.height = Math.round(im.height * k); c.getContext("2d").drawImage(im, 0, 0, c.width, c.height); res(c.toDataURL("image/jpeg", .7)); }; im.onerror = () => res(null); im.src = d; })))
    .then(th => { req.photos = th.filter(Boolean); addReq(req); SELL.done = n; SELL.photos = []; SELL.n = SELL.p = ""; renderSell(); });
});''')

# ---------- strings ----------
rep('/* ===== Language, routing, boot ===== */', '''Object.assign(T.en, {
  r_multi:"Pick everything that's broken", r_count:"{n} selected", r_none:"Pick one or more repairs", r_next:"See price",
  sp_lab:"Photos of your device (optional)", sp_cam:"Take photo", sp_lib:"Add photos", sp_more:"Add more", sp_hint:"Front, back and any damage. Up to {n} photos. We'll send a firmer offer with photos.",
  sp_alt:"Photo {n} of your device", sp_rm:"Remove photo {n}", sp_max:"Up to {n} photos", sp_bad:"That file isn't a photo we can read",
  sp_phone:"Phone or WhatsApp", sp_send:"Send {n} photo(s) and get an offer", sp_req:"Buyback offer, condition: {k}", sp_count:"{n} photo(s)",
  sp_done_t:"Thanks, {n}!", sp_done:"We've got your photos. You'll get an offer on WhatsApp, usually within an hour during opening hours.",
  sell_btn_alt:"Or ask on WhatsApp instead", via_sell:"Buyback"
});
Object.assign(T.de, {
  r_multi:"Wähle alles, was kaputt ist", r_count:"{n} ausgewählt", r_none:"Eine oder mehrere Reparaturen wählen", r_next:"Preis ansehen",
  sp_lab:"Fotos vom Gerät (optional)", sp_cam:"Foto aufnehmen", sp_lib:"Fotos hinzufügen", sp_more:"Weitere", sp_hint:"Vorderseite, Rückseite und Schäden. Bis zu {n} Fotos. Mit Fotos wird unser Angebot genauer.",
  sp_alt:"Foto {n} deines Geräts", sp_rm:"Foto {n} entfernen", sp_max:"Höchstens {n} Fotos", sp_bad:"Diese Datei können wir nicht als Foto lesen",
  sp_phone:"Telefon oder WhatsApp", sp_send:"{n} Foto(s) senden und Angebot holen", sp_req:"Ankauf-Angebot, Zustand: {k}", sp_count:"{n} Foto(s)",
  sp_done_t:"Danke, {n}!", sp_done:"Deine Fotos sind da. Du bekommst unser Angebot per WhatsApp, meist innerhalb einer Stunde während der Öffnungszeiten.",
  sell_btn_alt:"Oder lieber per WhatsApp fragen", via_sell:"Ankauf"
});
/* ===== Language, routing, boot ===== */''')
rep('fine_sell:"The WhatsApp offer is non-binding. Our {a} apply to purchases; see also our {p}."',
    'fine_sell:"Offers are non-binding until we have seen the device. We only use your photos and number for this offer and delete the photos after 30 days if you don\'t sell. Our {a} apply to purchases; see also our {p}."')
rep('fine_sell:"Das Angebot per WhatsApp ist unverbindlich. Für den Ankauf gelten unsere {a}; siehe auch {p}."',
    'fine_sell:"Angebote sind unverbindlich, bis wir das Gerät gesehen haben. Fotos und Nummer nutzen wir nur für dieses Angebot und löschen die Fotos nach 30 Tagen, wenn du nicht verkaufst. Für den Ankauf gelten unsere {a}; siehe auch {p}."')

# ---------- CSS ----------
rep('</style>', open('feedback.css', encoding='utf-8').read() + '\n</style>')

# controllers: TMR sticks and the other controller repairs as big cards
rep('console:["hdmi","fan","drift","display","drive","psu"] };', 'console:["hdmi","fan","drift","tmr","display","drive","psu","cport","battery","buttons"] };')
rep('sell_p:"We buy phones, tablets, laptops and consoles. Tell us what you have and get an offer on WhatsApp.",',
    'sell_p:"We buy phones, tablets, laptops and consoles. Tell us what you have, add a few photos and get an offer on WhatsApp.",')
rep('sell_p:"Wir kaufen Handys, Tablets, Laptops und Konsolen. Sag uns, was du hast, und hol dir ein Angebot per WhatsApp.",',
    'sell_p:"Wir kaufen Handys, Tablets, Laptops und Konsolen. Sag uns, was du hast, schick ein paar Fotos mit und hol dir ein Angebot per WhatsApp.",')

# ---------- the client's own TipTop logo (cropped from the shop sign photo) ----------
rep('''    <svg viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="10" fill="#3048F0"/><text x="20" y="26.6" text-anchor="middle" fill="#fff" style="font:800 16px Archivo,Arial,sans-serif;font-stretch:118%">TT</text><circle cx="32.5" cy="7.5" r="3.2" fill="#FFE14D"/></svg>
    <b>TipTop <span>Service 24</span></b>''',
    '''    <img class="logo-full" src="img/logo-tiptop.svg" alt="" width="188" height="40">
    <img class="logo-mark" src="img/logo-mark.svg" alt="" width="40" height="40">
    <b><span>Service 24</span></b>''')
rep('<meta name="description"', '<link rel="icon" href="img/logo-mark-180.png">\n<link rel="apple-touch-icon" href="img/logo-mark-180.png">\n<meta name="description"')

# ---------- shop section redesign (17 Nov 2026): open status on the photo, hours, colour cards for the three ways ----------
rep("globe:'", "clock:'<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M12 7v5.2l3.4 2\"/>', ship:'<path d=\"M3.5 7.5 12 3l8.5 4.5v9L12 21l-8.5-4.5z\"/><path d=\"M3.5 7.5 12 12l8.5-4.5M12 12v9\"/>', globe:'")
