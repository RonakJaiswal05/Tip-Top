/* TipTop Service 24: page script, ported from the approved prototype (prototype/index.html).
   The markup is rendered by Django; this file adds behaviour: price calculator, describe box with voice input,
   live open status, sell offer, before/after slider, motion, forms, cookie consent. No framework, no build step.
   Catalogue data comes from /api/catalog.json, texts and shop data from the #tt-data block in the page. */
(() => {
"use strict";
const D = JSON.parse(document.getElementById("tt-data").textContent);
const lang = D.lang;
const TX = D.t || {};
const WA_NUMBER = D.wa;
const URLS = D.urls || {};
const LS = {
  get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
};
function t(k, v) {
  let s = TX[k]; if (s == null) return k;
  if (v && typeof s === "string") for (const x in v) s = s.split("{" + x + "}").join(v[x]);
  return s;
}
const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmt = n => new Intl.NumberFormat(lang === "de" ? "de-DE" : "en-IE", {style:"currency", currency:"EUR", maximumFractionDigits:0}).format(n);
const norm = s => " " + s.toLowerCase().replace(/[’']/g, " ").replace(/[()“”„"\.,!?;:/]/g, " ").replace(/\s+/g, " ").trim() + " ";
const $ = id => document.getElementById(id);
const on = (id, ev, fn, opt) => { const el = $(id); if (el) el.addEventListener(ev, fn, opt); return el; };
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const ANIM = !reduce;
if (ANIM) document.documentElement.classList.add("anim");
let cmpSet = () => {};

const IC = {
  display:'<rect x="6" y="2.5" width="12" height="19" rx="2.4"/><path d="M9.5 7l2.5 3.5-2 2.5 3.5 3.5"/>',
  battery:'<rect x="2.5" y="7.5" width="17" height="9" rx="1.8"/><path d="M21.5 10.5v3M6 10.5v3M9.5 10.5v3"/>',
  port:'<path d="M9 3v5M15 3v5M7 8h10v3.5a5 5 0 0 1-10 0z"/><path d="M12 16.5V21"/>',
  back:'<rect x="6" y="2.5" width="12" height="19" rx="2.4"/><rect x="8.3" y="5" width="4.4" height="4.4" rx="1.2"/>',
  camera:'<path d="M4 7.5h3l2-2.5h6l2 2.5h3v11H4z"/><circle cx="12" cy="13" r="3.2"/>',
  camglass:'<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3.5"/><path d="M8 6.5l2 2.5"/>',
  frontcam:'<rect x="6" y="2.5" width="12" height="19" rx="2.4"/><circle cx="12" cy="5.6" r="1"/>',
  faceid:'<path d="M4 8V5.5A1.5 1.5 0 0 1 5.5 4H8M16 4h2.5A1.5 1.5 0 0 1 20 5.5V8M20 16v2.5a1.5 1.5 0 0 1-1.5 1.5H16M8 20H5.5A1.5 1.5 0 0 1 4 18.5V16M9 9.5v1M15 9.5v1M12 9.5v3.5h-1M9 15.5c2 1.5 4 1.5 6 0"/>',
  speaker:'<path d="M4 9h3.5L13 5v14l-5.5-4H4z"/><path d="M16.5 9a4 4 0 0 1 0 6M19 6.5a7.5 7.5 0 0 1 0 11"/>',
  earpiece:'<path d="M8 15c0 2.5 1.6 4 3.5 4S15 17.6 15 15.5c0-2.6 3-3.3 3-7.5a6 6 0 0 0-12 0"/>',
  mic:'<path d="M12 3a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V6a3 3 0 0 1 3-3z"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>',
  water:'<path d="M12 3s6 6.8 6 11a6 6 0 0 1-12 0c0-4.2 6-11 6-11z"/>',
  mainboard:'<rect x="7" y="7" width="10" height="10" rx="1.2"/><path d="M10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4"/>',
  data:'<ellipse cx="12" cy="6" rx="7.5" ry="2.8"/><path d="M4.5 6v12c0 1.6 3.4 2.8 7.5 2.8s7.5-1.2 7.5-2.8V6M4.5 12c0 1.6 3.4 2.8 7.5 2.8s7.5-1.2 7.5-2.8"/>',
  diagnosis:'<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5.5 5.5"/>',
  software:'<path d="M8 8l-4 4 4 4M16 8l4 4-4 4M13.5 5.5l-3 13"/>',
  buttons:'<path d="M12 3v7.5"/><path d="M7.2 6.3a7.5 7.5 0 1 0 9.6 0"/>',
  vibration:'<rect x="8" y="4.5" width="8" height="15" rx="1.8"/><path d="M4.5 9v6M19.5 9v6"/>',
  sim:'<path d="M7 3h7l4 4v14H7z"/><rect x="9.5" y="11.5" width="6" height="6" rx="1"/>',
  jack:'<path d="M4 15.5V12a8 8 0 0 1 16 0v3.5"/><rect x="3" y="14.5" width="4" height="6" rx="1.2"/><rect x="17" y="14.5" width="4" height="6" rx="1.2"/>',
  keyboard:'<rect x="2.5" y="6.5" width="19" height="11" rx="1.8"/><path d="M6 10h.01M9 10h.01M12 10h.01M15 10h.01M18 10h.01M7.5 14h9"/>',
  trackpad:'<rect x="4" y="4" width="16" height="16" rx="2.5"/><path d="M4 15h16M12 15v5"/>',
  hinge:'<path d="M5 4h14v10H5z"/><path d="M3 17h18"/>',
  fan:'<circle cx="12" cy="12" r="1.8"/><path d="M12 10.2c0-4 2.5-6.2 4.8-4.6 1.9 1.4.4 4.4-3.1 5.2M13.8 12c4 0 6.2 2.5 4.6 4.8-1.4 1.9-4.4.4-5.2-3.1M12 13.8c0 4-2.5 6.2-4.8 4.6-1.9-1.4-.4-4.4 3.1-5.2M10.2 12c-4 0-6.2-2.5-4.6-4.8 1.4-1.9 4.4-.4 5.2 3.1"/>',
  ssd:'<rect x="3" y="7" width="18" height="10" rx="1.6"/><path d="M6.5 11h5M6.5 13.5h3"/>',
  hdmi:'<path d="M3 8h18v4.5L18 16H6l-3-3.5z"/><path d="M7 11h10"/>',
  drive:'<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="2.2"/>',
  psu:'<path d="M13 2.5L5 13.5h6l-1 8 8-11h-6z"/>',
  drift:'<circle cx="12" cy="7" r="3.5"/><path d="M12 10.5V16M5 16h14v4H5z"/>',
  wa:'<path d="M4 20l1.3-3.9A8 8 0 1 1 8.2 19z"/><path d="M9 9.5c0 2.8 2.2 5 5 5l1.2-1.4-2-1-.8.8a3.5 3.5 0 0 1-1.8-1.8l.8-.8-1-2z"/>',
  call:'<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
  store:'<path d="M4 10v10h16V10"/><path d="M3 10l2-6h14l2 6"/><path d="M10 20v-5h4v5"/>',
  search:'<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/>',
  x:'<path d="M6 6l12 12M18 6L6 18"/>', left:'<path d="M15 5l-7 7 7 7"/>', right:'<path d="M9 5l7 7-7 7"/>', lr:'<path d="M9 6l-6 6 6 6M15 6l6 6-6 6"/>',
  check:'<path d="M5 12.5l4.5 4.5L19 7.5"/>', clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5.2l3.4 2"/>', ship:'<path d="M3.5 7.5 12 3l8.5 4.5v9L12 21l-8.5-4.5z"/><path d="M3.5 7.5 12 12l8.5-4.5M12 12v9"/>', globe:'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.6 3.8 5.6 3.8 9s-1.2 6.4-3.8 9M12 3C9.4 5.6 8.2 8.6 8.2 12s1.2 6.4 3.8 9"/>', plus:'<path d="M12 5v14M5 12h14"/>', img:'<rect x="3" y="4" width="18" height="16" rx="2.5"/><circle cx="9" cy="10" r="2"/><path d="M21 16l-5-5-9 9"/>'
};
const ic = (k, sw = 1.8) => `<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${IC[k] || IC.diagnosis}</svg>`;

/* ===== Images: responsive AVIF/WebP/JPEG from the media library (sizes as in the prototype) ===== */
const IMG = D.img || {};
const CAT_IMG = { phone:"cat-phone", tablet:"cat-tablet", laptop:"cat-laptop", console:"cat-console" };
// Repair photos per device type (client, 17 and 25 Nov 2026): the iPhone set only for Apple phones, the Android set for
// every other phone, own sets for tablets, laptops and consoles. Without a photo the card is a tile in the device colour.
function repImg(cat, k, brand) {
  const g = CAT && CAT.rimg ? CAT.rimg[cat === "phone" && brand === "Apple" ? "phone_apple" : cat] : null;
  const id = g && g[k];
  return id && IMG[id] ? id : null;
}
function ph(id, cls = "") { return `<figure class="ph ${cls}" data-img="${esc(id)}" aria-hidden="true"></figure>`; }
function imgSizes(f) {
  if (f.closest(".tile")) return "(max-width:599px) 44vw, (max-width:900px) 22vw, 200px";
  if (f.closest(".rep")) return "(max-width:520px) 76vw, (max-width:900px) 46vw, 440px";
  if (f.closest(".hero-frame")) return "(max-width:599px) 92vw, (max-width:900px) 40vw, 600px";
  if (f.closest(".lcard")) return "(max-width:599px) 84vw, (max-width:760px) 92vw, 700px";
  if (f.closest(".cmp")) return "(max-width:1400px) 96vw, 1400px";
  if (f.closest(".mini")) return "44px";
  if (f.closest(".rc")) return "160px";
  return "(max-width:700px) 92vw, 640px";
}
function hydrate(root = document) {
  root.querySelectorAll(".ph[data-img]:not(.tried)").forEach(f => {
    f.classList.add("tried");
    const m = IMG[f.dataset.img];
    if (!m || !m.s) return;
    const l = m.l || m.s, sizes = imgSizes(f);
    const set = x => m.s[x] ? (l === m.s ? `${m.s[x]} ${m.s.w}w` : `${m.s[x]} ${m.s.w}w, ${l[x]} ${l.w}w`) : "";
    const pic = document.createElement("picture");
    for (const x of ["avif", "webp"]) if (m.s[x]) { const so = document.createElement("source"); so.type = "image/" + x; so.srcset = set(x); so.sizes = sizes; pic.appendChild(so); }
    const im = document.createElement("img");
    im.alt = ""; im.decoding = "async";
    const eager = f.closest(".hero") || f.closest(".bld");
    if (eager) im.fetchPriority = f.closest(".hero-frame") ? "high" : "auto"; else im.loading = "lazy";
    im.onload = () => f.classList.add("loaded");
    im.onerror = () => pic.remove();
    if (m.fx != null && (m.fx !== 50 || m.fy !== 50)) im.style.objectPosition = m.fx + "% " + m.fy + "%";
    im.sizes = sizes; im.srcset = set("jpg"); im.src = l.jpg;
    pic.appendChild(im); f.appendChild(pic);
  });
}

/* ===== Catalogue: models, repairs and prices from the admin (JSON endpoint) ===== */
const CATS = ["phone", "tablet", "laptop", "console"];
let CAT = null, MODELS = {}, ALIASES = [], catP = null;
function loadCatalog() {
  if (!catP) catP = fetch(D.api.catalog, { credentials:"same-origin" }).then(r => { if (!r.ok) throw new Error("catalog"); return r.json(); })
    .then(c => { CAT = c; Object.assign(IMG, c.img || {}); buildModels(); return c; }).catch(e => { catP = null; throw e; });
  return catP;
}
function buildModels() {
  MODELS = {};
  for (const c of CATS) MODELS[c] = [];
  for (const m of CAT.models) if (MODELS[m.cat]) MODELS[m.cat].push({ id:String(m.id), cat:m.cat, brand:m.brand, name:m.name, loc:lang === "de" ? m.nde : m.nen, full:m[lang], slug:m.slug, fl:m.fl || "", ct:m.ct || "", no:m.no || [] });
  ALIASES = [];
  // Single everyday words never count as a model name on their own ("book a repair" is not a Surface Book).
  const seen = new Set();
  const add1 = (a, m) => { const k = a + "|" + m.id; if (a.length >= 3 && !ALIAS_STOP.has(a) && !/^phone \d/.test(a) && !seen.has(k)) { seen.add(k); ALIASES.push({ a, m }); } };
  // Each alias also counts with "+" written as "plus" and with a space between letters and numbers ("note 20", "z fold 5").
  const add = (a, m) => { a = norm(a).trim(); for (const v of [a, a.replace(/\+/g, " plus"), a.replace(/([a-z])(\d)/g, "$1 $2"), a.replace(/([a-z])(\d)/g, "$1 $2").replace(/\+/g, " plus")]) add1(v.replace(/\s+/g, " ").trim(), m); };
  for (const c of CATS) for (const m of MODELS[c]) {
    const n = norm(m.name).trim();
    add(m.name, m); add(m.brand + " " + m.name, m);
    add(n.replace(/([a-z])\s(\d)/g, "$1$2"), m);
    if (m.brand === "Samsung" && m.cat !== "laptop") add(n.replace(/^galaxy /, ""), m);
    if (/^playstation \d/.test(n)) add(n.replace(/^playstation /, "ps"), m);
    if (n === "playstation portal") add("ps portal", m);
    if (/^xbox (series|one)/.test(n)) add(n.replace(/^xbox /, ""), m);
    if (n === "dualsense controller") { add("ps5 controller", m); add("playstation 5 controller", m); }
    if (/ controller$/.test(n)) { const s2 = n.replace(/ controller$/, ""); if (s2.includes(" ") || s2 === "dualsense") add(s2, m); }
    if (/^iphone \d/.test(n)) { add(n.replace(/^iphone /, "ip"), m); add(n.replace(/^iphone /, "ip "), m); }
    if (/^dualshock 4/.test(n)) { add("ps4 controller", m); add("playstation 4 controller", m); }
    if (m.name === "iPhone Duo") { add("iphone fold", m); add("iphone foldable", m); }
    const g = m.name.match(/^(iPad(?: mini| Air| Pro(?: [\d.]+)?)?) \((\d+)(?:st|nd|rd|th) gen\)$/);
    if (g) { add(g[1] + " " + g[2], m); add(g[1] + " " + g[2] + " gen", m); add(g[1] + " " + g[2] + " generation", m); add(g[1] + " " + g[2] + ". generation", m); }
  }
}
const ALIAS_STOP = new Set(["one","book","modern","stealth","raider","swift","precision","prestige"]);
const brandsOf = c => [...new Set(MODELS[c].map(m => m.brand))];
const svName = (k, cat) => { const r = CAT && CAT.rep[k]; if (!r) return k; const o = (r.n && r.n[cat]) || r; return o[lang]; };
const locName = m => m.custom ? m.name : m.loc;
const fullName = m => m.custom ? m.name : m.full;
function servicesFor(m) {
  if (!m || !CAT) return [];
  const lists = CAT.lists[m.cat] || {};
  if (m.custom) return (lists[""] || []).map(x => x[0]);
  const rows = m.cat === "console" ? (lists[m.ct] || lists[""] || []) : (lists[""] || []);
  // Repairs a model physically can't have (no fan, soldered storage, AA batteries) are switched off per model in the admin.
  return rows.filter(([k, req]) => !(req === "face_id" && !m.fl.includes("F")) && !(req === "jack" && !m.fl.includes("J")) && !m.no.includes(k)).map(x => x[0]);
}
function price(m, key, tier) {
  const pick = v => v == null ? null : typeof v === "object" ? (v[tier === "o" ? "o" : "p"] == null ? null : v[tier === "o" ? "o" : "p"]) : v;
  if (!m.custom) { const v = (CAT.prices[m.id] || {})[key]; if (v != null) return pick(v); }
  const r = CAT.rep[key];
  if (r && r.fix) return pick((CAT.base[m.cat] || {})[key]);
  return null;
}
function isFrom(m, key) {
  if (!m.custom && CAT.prices[m.id] && key in CAT.prices[m.id]) return (CAT.from[m.id] || []).includes(key);
  const r = CAT.rep[key]; return !!(r && r.from);
}
function priceLabel(m, key) {
  if (CAT.rep[key] && CAT.rep[key].tiers) {
    const p = price(m, key, "p"), o = price(m, key, "o");
    if (p == null && o == null) return t("on_request");
    return t("from") + " " + fmt(Math.min(p == null ? Infinity : p, o == null ? Infinity : o));
  }
  const v = price(m, key);
  if (v == null) return t("on_request");
  return (isFrom(m, key) ? t("from") + " " : "") + fmt(v);
}
function totalOf(m, sel) {
  let sum = 0, unknown = 0, from = false;
  for (const s of sel) { const v = price(m, s.key, s.tier); if (v == null) unknown++; else sum += v; if (isFrom(m, s.key)) from = true; }
  if (unknown && unknown === sel.length) return { text:t("on_request"), sum:null };
  const text = (from ? t("from") + " " : "") + fmt(sum);
  return { text, sum, from, extra:unknown ? t("plus_req") : "" };
}

/* ===== Smart assistant (text + voice), runs in the browser only ===== */
const KW = [
  ["camglass",["camera glass","kameraglas","camera lens","kameralinse","linse"]],
  ["frontcam",["front camera","selfie","frontkamera"]],
  ["faceid",["face id","faceid","gesichtserkennung"]],
  ["tmr",["tmr","hall effect","hall-effect","hall sensor","hall stick"]],
  ["drift",["drift","joystick","stick"]],
  ["hdmi",["hdmi","no picture","no signal","kein bild","kein signal"]],
  ["drive",["disc","disk","laufwerk","blu-ray","bluray"]],
  ["keyboard",["keyboard","tastatur"]],
  ["trackpad",["trackpad","touchpad"]],
  ["hinge",["hinge","scharnier"]],
  ["water",["water","wet","liquid","toilet","pool","coffee","rain","drink","wasser","nass","flüssig","getränk","kaffee","regen"]],
  ["data",["data","recover","backup","daten","fotos retten","bilder retten","datenrettung"]],
  ["battery",["dead battery","battery is dead","battery dead","akku leer","akku ist leer","battery","akku","drains","dies fast","swollen","batterie","aufgebläht","hält nicht","entlädt"]],
  ["earpiece",["earpiece","hörmuschel","can t hear the caller","can t hear people","höre den anderen nicht","höre nichts beim telefonieren"]],
  ["mic",["microphone","mic","mikrofon","can t hear me","hört mich nicht","versteht mich nicht"]],
  ["speaker",["speaker","sound","music","lautsprecher","ton","klang","leise"]],
  ["fan",["fan","noisy","overheat","overheating","hot","lüfter","zu laut","sehr laut","heiß","heiss","überhitz"]],
  ["ssd",["ssd","storage full","slow","langsam","speicher voll","upgrade"]],
  ["psu",["power supply","netzteil"]],
  ["port",["charging","charge","charger","port","cable","lightning","usb-c","usb","lädt","ladebuchse","ladekabel","ladeanschluss"]],
  ["back",["back glass","back cover","backcover","rückseite","housing","gehäuse"]],
  ["camera",["camera","kamera","blurry","unscharf"]],
  ["vibration",["vibrat"]],
  ["sim",["sim"]],
  ["jack",["headphone","aux","kopfhörer","klinke"]],
  ["buttons",["power button","volume button","button","taste","knopf","keys","key"]],
  ["software",["software","update","apple logo","logo","boot","frozen","stuck","hängt","virus","firmware","reset"]],
  ["mainboard",["won t turn on","wont turn on","doesn t turn on","not turning on","won t start","no power","dead","startet nicht","geht nicht an","geht nicht mehr an","tot","mainboard","motherboard","logic board","platine"]],
  ["display",["screen","display","glass","cracked","crack","smashed","black screen","touch","lines","flicker","bildschirm","glas","gesprungen","riss","zersprungen","kaputt display","schwarz","streifen","flackert"]]
];
const CATW = {
  phone:["handy","phone","smartphone","iphone","galaxy","pixel","redmi","xperia","mobile","telefon","samsung","xiaomi","huawei","oneplus","oppo","motorola","moto","razr","honor","nothing phone","cmf phone","fairphone","realme"],
  tablet:["ipad","tablet","tablette","galaxy tab","tab","pad","matepad"],
  laptop:["laptop","notebook","macbook","thinkpad","computer","rechner","surface","ideapad","zenbook","vivobook"],
  console:["console","konsole","playstation","ps5","ps4","xbox","switch","nintendo","steam deck","controller","gamepad","dualsense","joy-con","rog ally","legion go","msi claw","playstation portal","ps3","xbox one","xbox 360","handheld"]
};
const BRANDW = [["Apple",["iphone","ipad","macbook","apple"]],["Samsung",["samsung","galaxy"]],["Google",["pixel","google"]],["Xiaomi",["xiaomi","redmi","poco"]],["Huawei",["huawei"]],["OnePlus",["oneplus"]],["Oppo",["oppo"]],["Motorola",["motorola","moto","razr"]],["Honor",["honor"]],["Nothing",["nothing phone","cmf"]],["Fairphone",["fairphone"]],["Realme",["realme"]],["Sony",["sony","xperia","playstation","ps5","ps4","dualsense"]],["Microsoft",["xbox","surface","microsoft"]],["Nintendo",["nintendo","switch","joy-con"]],["Valve",["steam deck"]],["Lenovo",["lenovo","thinkpad","legion"]],["HP",["hp"]],["Dell",["dell"]],["ASUS",["asus","rog"]],["Acer",["acer"]],["MSI",["msi"]]];
const reEsc = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const hasW = (s, w) => new RegExp("(^|\\s)" + reEsc(w) + (w.length <= 3 ? "(?=\\s|$)" : "")).test(s);
function parse(text) {
  let s = norm(text);
  let best = null;
  for (const a of ALIASES) if ((!best || a.a.length > best.a.length) && s.includes(" " + a.a + " ")) best = a;
  let m = best ? best.m : null;
  if (best) s = s.replace(" " + best.a + " ", " ");
  if (m && m.cat === "console" && /controller|gamepad/.test(s) && !m.fl.includes("P")) {
    const pad = MODELS.console.find(x => x.brand === m.brand && x.fl.includes("P")); if (pad) m = pad;
  }
  let rest = s; const keys = [];
  for (const [k, kws] of KW) for (const kw of kws) {
    const re = new RegExp("(^|\\s)" + reEsc(kw) + (kw.length <= 3 ? "(?=\\s|$)" : ""));
    if (re.test(rest)) { if (!keys.includes(k)) keys.push(k); rest = rest.replace(re, " "); }
  }
  if (keys.includes("tmr") && keys.includes("drift")) keys.splice(keys.indexOf("drift"), 1);
  // A one-word model name loses against an explicit device word for another category ("power switch on my laptop").
  if (m && !best.a.includes(" ")) {
    const other = ["tablet","laptop","console","phone"].find(c => c !== m.cat && CATW[c].some(w => w !== best.a && hasW(norm(text), w)));
    if (other) m = null;
  }
  let cat = m ? m.cat : null, brand = m ? m.brand : null;
  const full = norm(text);
  if (!cat) {
    for (const c of ["tablet","laptop","console","phone"]) if (CATW[c].some(w => hasW(full, w))) { cat = c; break; }
    if (!cat) { if (keys.some(k => ["keyboard","trackpad","hinge"].includes(k))) cat = "laptop"; else if (keys.some(k => ["hdmi","drive","drift","psu"].includes(k))) cat = "console"; else if (keys.includes("faceid")) cat = "phone"; }
  }
  // Same word, different repair per device: "Ladebuchse" on a console is the controller/handheld port, "Tasten" on a laptop is the keyboard.
  if (cat === "console") { const i = keys.indexOf("port"); if (i >= 0) keys.includes("cport") ? keys.splice(i, 1) : keys.splice(i, 1, "cport"); }
  if (cat === "laptop") { const i = keys.indexOf("buttons"); if (i >= 0) keys.includes("keyboard") ? keys.splice(i, 1) : keys.splice(i, 1, "keyboard"); }
  if (cat && !brand) for (const [b, ws] of BRANDW) if (ws.some(w => hasW(full, w)) && MODELS[cat].some(x => x.brand === b)) { brand = b; break; }
  return { m, cat, brand, keys:keys.slice(0, 3) };
}

function startVoice(btn, onText, say) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { say(t("ai_unsup")); return; }
  let rec;
  try { rec = new SR(); } catch (e) { say(t("ai_blocked")); return; }
  rec.lang = lang === "de" ? "de-DE" : "en-GB"; rec.interimResults = true; rec.maxAlternatives = 1;
  let finalText = "";
  btn.classList.add("rec"); say(t("ai_listen"));
  rec.onresult = ev => { let txt = ""; for (const res of ev.results) txt += res[0].transcript; finalText = txt; onText(txt, false); };
  rec.onerror = ev => { btn.classList.remove("rec"); say(ev.error === "not-allowed" || ev.error === "service-not-allowed" || ev.error === "audio-capture" ? t("ai_blocked") : t("ai_unsup")); };
  rec.onend = () => { btn.classList.remove("rec"); if (finalText) onText(finalText, true); };
  try { rec.start(); } catch (e) { btn.classList.remove("rec"); say(t("ai_blocked")); }
}

/* ===== Live open status per shop, from the opening hours, special hours and holidays in the admin ===== */
const OPEN = {}; for (const o of D.open || []) OPEN[o.key] = o.iv;
const BP = new Intl.DateTimeFormat("en-GB", { timeZone:"Europe/Berlin", year:"numeric", month:"2-digit", day:"2-digit", weekday:"short", hour:"2-digit", minute:"2-digit", hourCycle:"h23" });
function bParts(ms) {
  const p = BP.formatToParts(new Date(ms)), g = ty => (p.find(x => x.type === ty) || {}).value;
  return { ymd:g("year") + g("month") + g("day"), wd:["Sun","Mon","Tue","Wed","Thu","Fri","Sat"].indexOf(g("weekday")), h:+g("hour"), m:+g("minute") };
}
const hm = (h, m) => lang === "de" ? (m ? h + ":" + String(m).padStart(2, "0") : String(h)) : String(h).padStart(2, "0") + ":" + String(m).padStart(2, "0");
function openStatus(key) {
  const iv = OPEN[key] || [], now = Date.now();
  for (const [a, b] of iv) {
    if (a <= now && now < b) { const e = bParts(b); return { open:true, text:t("open", { t:hm(e.h, e.m) }) }; }
    if (a > now) {
      const s = bParts(a), n = bParts(now);
      const label = s.ymd === n.ymd ? t("today") : s.ymd === bParts(now + 864e5).ymd ? t("tomorrow") : t("days")[s.wd];
      return { open:false, text:t("closed", { d:label, t:hm(s.h, s.m) }) };
    }
  }
  return { open:false, text:t("closed_now") };
}
function updStatus() {
  document.querySelectorAll("[data-open]").forEach(el => {
    const st = openStatus(el.dataset.open);
    el.innerHTML = `<span class="pulse${st.open ? "" : " off"}"></span>${esc(st.text)}`;
  });
}

/* ===== Talking to the server: requests, beacons, consent ===== */
function csrf() { const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/); return m ? decodeURIComponent(m[1]) : ""; }
async function send(kind, payload) {
  const body = Object.assign({ kind, lang, source:location.pathname, ts:D.ts }, payload);
  const r = await fetch(D.api.request, { method:"POST", credentials:"same-origin", headers:{ "Content-Type":"application/json", "Accept":"application/json", "X-CSRFToken":csrf() }, body:JSON.stringify(body) });
  let j = {}; try { j = await r.json(); } catch (e) {}
  if (!r.ok) { const err = new Error(j.error || "send"); err.status = r.status; err.data = j; throw err; }
  return j;
}
function beacon(kind, payload) {
  try {
    fetch(D.api.request, { method:"POST", credentials:"same-origin", keepalive:true, headers:{ "Content-Type":"application/json", "X-CSRFToken":csrf() },
      body:JSON.stringify(Object.assign({ kind, lang, source:location.pathname, ts:D.ts }, payload)) }).catch(() => {});
  } catch (e) {}
}
const sendErr = err => err && err.status === 429 ? t("err_rate") : t("err_send");
const waLink = msg => `https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(msg)}`;
let toastT;
function toast(msg) { const el = $("toast"); el.textContent = msg; el.classList.add("show"); clearTimeout(toastT); toastT = setTimeout(() => el.classList.remove("show"), 2800); }
function copyText(txt, okMsg) {
  try { navigator.clipboard.writeText(txt).then(() => toast(okMsg), () => toast(txt.slice(0, 120))); } catch (e) { toast(txt.slice(0, 120)); }
}
function fine(k) {
  return esc(t(k)).replace("{p}", `<a href="${URLS.datenschutz}">${esc(t("lk_priv"))}</a>`).replace("{a}", `<a href="${URLS.agb}">${esc(t("lk_agb"))}</a>`);
}
function devTiles(attr) {
  return CATS.map(c => `<button type="button" class="dev" ${attr}="${c}" style="--cc:var(--c-${c})"><span class="tile">${ph(CAT_IMG[c], "notag")}</span><b>${esc(t("cat_" + c))}${ic("right", 2.4)}</b><small>${esc(t("cat_" + c + "_s"))}</small></button>`).join("");
}
const repData = (m, sel) => sel.map(s => { const v = price(m, s.key, s.tier); return { key:s.key, tier:s.tier || "", name:svName(s.key, m.cat), price:v, from:isFrom(m, s.key) }; });

/* ===== Repair builder (price calculator) ===== */
const B = { step:1, cat:null, model:null, brand:"all", q:"", sel:[], pending:[], showAll:false, other:false, act:null, name:"", phone:"", done:null, hoverKey:null, lastFocus:null };
const HASH = lang === "de" ? "rechner" : "calculator";
const topOf = cat => (CAT && CAT.top[cat]) || [];

async function openBuilder(opts = {}) {
  const lastFocus = document.activeElement;
  if (!CAT) { try { await loadCatalog(); } catch (e) { toast(t("err_send")); return; } }
  Object.assign(B, { step:1, cat:null, model:null, brand:"all", q:"", sel:[], pending:[], showAll:false, other:false, act:null, done:null, hoverKey:null }, opts);
  if (B.model) B.cat = B.model.cat;
  if (!opts.step) B.step = B.model ? (B.sel.length ? 4 : 3) : B.cat ? 2 : 1;
  B.lastFocus = lastFocus;
  $("bld").hidden = false; lockScroll();
  renderB("f"); $("bldPanel").focus({ preventScroll:true });
}
function closeBuilder() {
  if ($("bld").hidden) return;
  $("bld").hidden = true; lockScroll();
  if (readHash()) history.replaceState(null, "", location.pathname + location.search);
  if (B.lastFocus && B.lastFocus.focus) B.lastFocus.focus({ preventScroll:true });
}
function goB(step, dir = "f") { B.step = step; B.act = null; renderB(dir); }
function sideImgId() {
  const ri = k => repImg(B.cat, k, B.model ? B.model.brand : "");
  if (B.hoverKey && ri(B.hoverKey)) return ri(B.hoverKey);
  const k = B.sel.map(s => s.key).reverse().find(x => ri(x));
  if (k) return ri(k);
  if (B.hoverKey && CAT_IMG[B.hoverKey]) return CAT_IMG[B.hoverKey];
  if (B.cat) return CAT_IMG[B.cat];
  return "hero";
}
function renderSide() {
  const id = sideImgId(), side = $("bldSide");
  const cur = side.querySelector(".ph");
  if (!cur || cur.dataset.img !== id) { side.innerHTML = ph(id, "notag") + `<div class="side-sum" id="sideSum"></div>`; }
  const m = B.model, tt = m && B.sel.length ? totalOf(m, B.sel) : null;
  $("sideSum").innerHTML = `<small>${esc(B.cat ? t("cat_" + B.cat) : t("steps")[0])}</small><h3>${esc(m ? fullName(m) : B.cat ? t("m_title") : t("side_empty"))}</h3>
    ${B.sel.length ? `<div class="side-tags">${B.sel.map(s => `<span>${esc(svName(s.key, B.cat))}</span>`).join("")}</div>` : ""}
    ${tt ? `<div class="side-price">${esc(tt.text)}</div>` : ""}`;
  const mini = $("bldMini");
  mini.innerHTML = `${ph(id, "notag")}<span>${esc(m ? fullName(m) : B.cat ? t("cat_" + B.cat) : t("side_empty"))}</span>${tt ? `<b>${esc(tt.text)}</b>` : ""}`;
  hydrate(side); hydrate(mini);
}
function renderB(dir = "n") {
  $("bldSteps").innerHTML = t("steps").map((n, i) => {
    const k = i + 1, done = k < B.step && !B.done, cur = k === B.step || (B.done && k === 4);
    return `<li class="${done ? "done" : ""}${cur ? " cur" : ""}"><button type="button" data-b="goto" data-v="${k}" ${done ? "" : "disabled"}${cur ? ' aria-current="step"' : ""}><span>${esc(n)}</span><i></i></button></li>`;
  }).join("");
  $("bldBack").disabled = B.step === 1 || !!B.done;
  $("bldPanel").style.setProperty("--cc", B.cat ? "var(--c-" + B.cat + ")" : "var(--ink)");
  const view = B.done ? vDone() : [null, vDev, vModel, vRepair, vPrice][B.step]();
  $("bldBody").innerHTML = `<div class="bv ${dir === "f" ? "f" : dir === "b" ? "b" : ""}">${view}</div>`;
  if (dir !== "n") $("bldBody").scrollTop = 0;
  renderSide(); renderFoot(); hydrate($("bldBody"));
  const tb = $("bTotal"); if (tb) { if (ANIM && B._tot && B._tot !== tb.textContent) tb.classList.add("bump"); B._tot = tb.textContent; } else B._tot = null;
  if (!$("bld").hidden && (document.activeElement === document.body || !document.activeElement || !$("bld").contains(document.activeElement))) $("bldPanel").focus({ preventScroll:true });
  if (B.step === 2 && dir !== "n" && matchMedia("(pointer:fine)").matches) { const s = $("bSearch"); if (s) s.focus({ preventScroll:true }); }
  writeHash();
}
function vDev() { return `<h2 class="bt">${esc(t("d_title"))}</h2><div class="devs">${devTiles("data-bcat")}</div>`; }
function modelList() {
  let list;
  if (B.q.trim()) {
    const q = norm(B.q).trim(), qq = q.replace(/\s/g, "");
    list = MODELS[B.cat].filter(m => { const n = norm(m.brand + " " + m.name).trim(); return n.includes(q) || n.replace(/\s/g, "").includes(qq); });
    if (!list.length) return `<p class="mnone">${esc(t("no_match", { q:B.q.trim() }))} <button type="button" class="lk" data-b="useq">${esc(t("use_q", { q:B.q.trim() }))}</button></p>`;
  } else if (B.brand === "all") list = MODELS[B.cat].filter(m => m.fl.includes("p"));
  else list = MODELS[B.cat].filter(m => m.brand === B.brand);
  return list.map(m => `<button type="button" data-b="model" data-v="${m.id}"><small>${esc(m.brand)}</small>${esc(locName(m))}</button>`).join("");
}
function vModel() {
  const brands = brandsOf(B.cat);
  return `<h2 class="bt">${esc(t("m_title"))}</h2>
    <label class="find">${ic("search", 2)}<span class="sr">${esc(t("search_ph"))}</span><input id="bSearch" type="search" placeholder="${esc(t("search_ph"))}" value="${esc(B.q)}" autocomplete="off"></label>
    <div class="brands" role="group">${[["all", t("popular")], ...brands.map(b => [b, b])].map(([v, l]) => `<button type="button" data-b="brand" data-v="${esc(v)}" aria-pressed="${!B.q && B.brand === v}">${esc(l)}</button>`).join("")}</div>
    <div class="mgrid" id="bModels">${modelList()}</div>
    ${B.other ? `<div class="other"><input class="inp" id="bOther" placeholder="${esc(t("other_ph"))}" aria-label="${esc(t("other_ph"))}"><button type="button" class="btn" data-b="useother">${esc(t("use_model"))}</button></div>` : `<p style="margin-top:14px"><button type="button" class="lk" data-b="other">${esc(t("not_listed"))}</button></p>`}
    <p class="tip">${esc(t("tip_" + B.cat))}</p>`;
}
function vRepair() {
  const m = B.model, all = servicesFor(m), top = topOf(m.cat).filter(k => all.includes(k)).slice(0, 6);
  const rest = all.filter(k => !top.includes(k));
  const on = k => B.sel.some(s => s.key === k);
  const card = k => { const im = repImg(m.cat, k, m.brand);
    return `<button type="button" class="rc" data-b="rep" data-v="${k}" data-hk="${k}" aria-pressed="${on(k)}"><span class="rc-m">${im ? ph(im) : `<span class="icon-tile">${ic((CAT.rep[k] && CAT.rep[k].icon) || k, 1.4)}</span>`}<span class="tick" aria-hidden="true">${ic("check", 2.8)}</span></span><b>${esc(svName(k, m.cat))}</b><small>${esc(priceLabel(m, k))}</small></button>`; };
  const restHtml = rest.length ? (B.showAll
      ? `<div class="rlist">${rest.map(k => `<button type="button" data-b="rep" data-v="${k}" data-hk="${k}" aria-pressed="${on(k)}"><span><i class="cb" aria-hidden="true">${ic("check", 2.8)}</i>${esc(svName(k, m.cat))}</span><span>${esc(priceLabel(m, k))}</span></button>`).join("")}</div><p class="morebtn"><button type="button" class="lk" data-b="all">${esc(t("fewer"))}</button></p>`
      : `<p class="morebtn"><button type="button" class="lk" data-b="all">${esc(t("all_rep", { n:all.length }))}</button></p>`) : "";
  const dg = price(m, "diagnosis");
  return `<h2 class="bt">${esc(t("r_title"))}</h2><p class="bs">${esc(fullName(m))} · ${esc(t("r_multi"))}</p>
    <div class="rgrid" style="--tc:var(--t-${m.cat});--cc:var(--c-${m.cat})">${top.map(card).join("")}</div>${restHtml}
    <button type="button" class="unsure" data-b="rep" data-v="diagnosis" data-hk="diagnosis" aria-pressed="${on("diagnosis")}"><span><b>${esc(t("unsure_t"))}</b><small>${esc(t("unsure_s", { p:dg == null ? t("on_request") : fmt(dg) }))}</small></span>${ic("diagnosis")}</button>`;
}
const tierName = s => CAT.rep[s.key] && CAT.rep[s.key].tiers ? " (" + t(s.tier === "o" ? "tier_o" : "tier_p") + ")" : "";
function bRepText() { return B.sel.map(s => svName(s.key, B.cat) + tierName(s)).join(", "); }
function waMsg(m) {
  const tt = totalOf(m, B.sel);
  return t("wa_msg", { d:fullName(m), r:B.sel.map(s => { const v = price(m, s.key, s.tier); return svName(s.key, m.cat) + tierName(s) + ": " + (v == null ? t("on_request") : fmt(v)); }).join(", "), t:tt.text });
}
function vPrice() {
  const m = B.model, tt = totalOf(m, B.sel), disp = B.sel.find(s => CAT.rep[s.key] && CAT.rep[s.key].tiers);
  const lines = B.sel.map((s, i) => { const v = price(m, s.key, s.tier); return `<div class="line"><span class="n">${esc(svName(s.key, m.cat))}${tierName(s) ? ` <span style="color:var(--muted);font-weight:500">(${esc(t(s.tier === "o" ? "tier_o" : "tier_p"))})</span>` : ""}</span><span class="p">${esc(v == null ? t("on_request") : (isFrom(m, s.key) ? t("from") + " " : "") + fmt(v))}</span><button type="button" class="rm" data-b="rm" data-i="${i}" aria-label="${esc(t("remove"))}">${ic("x", 2)}</button></div>`; }).join("");
  const tier = disp ? `<div class="tierbox"><div class="seg" role="group"><button type="button" data-b="tier" data-v="p" aria-pressed="${disp.tier !== "o"}">${esc(t("tier_p"))}</button><button type="button" data-b="tier" data-v="o" aria-pressed="${disp.tier === "o"}">${esc(t("tier_o"))}</button></div><p>${esc(t(disp.tier === "o" ? "tier_o_s" : "tier_p_s"))}</p></div>` : "";
  const cb = B.act === "cb" ? `<form class="sub" id="cbForm" novalidate><div class="two"><div><label class="lab-l" for="cbName">${esc(t("name_l"))}</label><input class="inp" id="cbName" autocomplete="name" value="${esc(B.name)}"></div><div><label class="lab-l" for="cbPhone">${esc(t("phone_l"))}</label><input class="inp" id="cbPhone" type="tel" autocomplete="tel" value="${esc(B.phone)}"></div></div><div class="hp" aria-hidden="true"><label for="cbWeb">Website</label><input id="cbWeb" name="website" tabindex="-1" autocomplete="off"></div><p class="err" id="cbErr" role="alert"></p><p class="fine">${fine("fine_cb")}</p><button type="submit" class="btn" style="justify-self:start">${esc(t("cb_send"))}</button></form>` : "";
  const wi = B.act === "wi" ? `<div class="sub">${(D.shops || []).map(sh => `<div class="mshop"><div><b>${esc(sh.area)}</b><small>${esc(sh.street)}, ${esc(openStatus(sh.key).text)}</small></div><a class="lk" href="${esc(sh.maps)}" target="_blank" rel="noopener">${esc(t("directions"))}</a></div>`).join("")}</div>` : "";
  const page = !m.custom && URLS.models ? `<p style="margin-top:10px"><a class="lk" href="${URLS.models}${m.slug}/">${esc(t("all_models"))}: ${esc(fullName(m))}</a></p>` : "";
  return `<h2 class="bt">${esc(t("p_title"))}</h2><p class="bs">${esc(fullName(m))}</p>
    <div class="lines">${lines}</div>
    <p style="margin-top:12px"><button type="button" class="lk" data-b="add">${esc(t("add"))}</button></p>
    ${tier}
    <div class="total"><span>${esc(t("total"))}</span><b id="bTotal">${esc(tt.text)}</b></div>
    <p class="vat">${esc(t("vat"))}${tt.extra ? " " + esc(t("plus_req")) : ""}</p>
    <div class="opts">
      <a class="opt wa" href="${waLink(waMsg(m))}" target="_blank" rel="noopener" data-b="wa">${ic("wa", 1.9)}<span><b>${esc(t("wa_b"))}</b><small>${esc(t("wa_s"))}</small></span></a>
      <button type="button" class="opt" data-b="cb" aria-expanded="${B.act === "cb"}">${ic("call")}<span><b>${esc(t("cb_b"))}</b><small>${esc(t("cb_s"))}</small></span></button>${cb}
      <button type="button" class="opt" data-b="wi" aria-expanded="${B.act === "wi"}">${ic("store")}<span><b>${esc(t("wi_b"))}</b><small>${esc(t("wi_s"))}</small></span></button>${wi}
    </div>
    <p class="fine bfine">${fine("fine_wa")}</p>${page}`;
}
function vDone() {
  return `<div class="ok"><span class="ck">${ic("check", 2.4)}</span><h2 class="bt">${esc(t("cb_done_t", { n:B.done }))}</h2><p class="bs">${esc(t("cb_done"))}</p><button type="button" class="btn" data-b="restart">${esc(t("restart"))}</button></div>`;
}
function renderFoot() {
  const f = $("bldFoot"), show = B.step === 3 && !B.done && !!B.model;
  f.hidden = !show; if (!show) { f.innerHTML = ""; return; }
  const n = B.sel.length, tt = n ? totalOf(B.model, B.sel) : null;
  f.innerHTML = `<span class="bf-t" aria-live="polite"><b>${esc(n ? t("r_count", { n }) : t("r_none"))}</b>${tt ? `<small>${esc(tt.text)}</small>` : ""}</span><button type="button" class="btn" data-b="next" ${n ? "" : "disabled"}>${esc(t("r_next"))}${ic("right", 2.2)}</button>`;
}
function toggleSel(key) {
  const i = B.sel.findIndex(s => s.key === key);
  if (i >= 0) B.sel.splice(i, 1); else addSel(key);
  $("bldBody").querySelectorAll(`[data-b="rep"][data-v="${key}"]`).forEach(x => x.setAttribute("aria-pressed", i < 0));
  renderFoot(); renderSide(); writeHash();
}
function addSel(key, tier) {
  const ex = B.sel.find(s => s.key === key);
  const tiered = CAT.rep[key] && CAT.rep[key].tiers;
  if (ex) { if (tier) ex.tier = tier; } else B.sel.push(tiered ? { key, tier:tier || "p" } : { key });
}
function chooseModel(m) {
  B.model = m; B.cat = m.cat;
  const valid = servicesFor(m);
  B.sel = B.sel.filter(s => s.key === "diagnosis" || valid.includes(s.key));
  B.pending.filter(k => k === "diagnosis" || valid.includes(k)).forEach(k => addSel(k));
  B.pending = [];
  goB(B.sel.length ? 4 : 3);
}
const slugify = s => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/\+/g, " plus ").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const customModel = n => ({ id:"custom-" + slugify(n), cat:B.cat, brand:"", name:n, fl:"", ct:"", custom:true });

/* deep links: #rechner, #rechner=phone, #rechner=apple-iphone-13, #rechner=apple-iphone-13/display:o,battery */
function readHash() {
  let h = location.hash.slice(1); try { h = decodeURIComponent(h); } catch (e) {}
  const m = h.match(/^(rechner|calculator)(?:=([^/]*)(?:\/(.*))?)?$/);
  return m ? { a:m[2] || "", r:m[3] || "" } : null;
}
function writeHash() {
  if ($("bld").hidden) return;
  let h = HASH;
  if (B.model && !B.model.custom && !B.done) { h += "=" + B.model.slug; if (B.sel.length) h += "/" + B.sel.map(s => s.key + (s.tier === "o" ? ":o" : "")).join(","); }
  else if (B.cat && !B.done) h += "=" + B.cat;
  if (location.hash !== "#" + h) history.replaceState(null, "", "#" + h);
}
async function fromHash() {
  const h = readHash(); if (!h) return;
  try { await loadCatalog(); } catch (e) { return; }
  const opts = {};
  if (CATS.includes(h.a)) opts.cat = h.a;
  else if (h.a) {
    const m = CATS.flatMap(c => MODELS[c]).find(x => x.slug === h.a);
    if (m) {
      opts.model = m;
      const valid = servicesFor(m);
      opts.sel = h.r.split(",").filter(Boolean).map(x => { const [k, tr] = x.split(":"); return { k, tr }; })
        .filter(x => x.k === "diagnosis" || valid.includes(x.k))
        .map(x => CAT.rep[x.k] && CAT.rep[x.k].tiers ? { key:x.k, tier:x.tr === "o" ? "o" : "p" } : { key:x.k });
    }
  }
  openBuilder(opts);
}

$("bld").addEventListener("click", e => {
  if (e.target.closest("[data-close]")) return closeBuilder();
  const cat = e.target.closest("[data-bcat]");
  if (cat) { const c = cat.dataset.bcat; if (B.cat !== c) { B.model = null; B.sel = []; } B.cat = c; B.brand = "all"; B.q = ""; B.other = false; return goB(2); }
  const b = e.target.closest("[data-b]"); if (!b) return;
  const a = b.dataset.b, v = b.dataset.v;
  switch (a) {
    case "goto": goB(+v, "b"); break;
    case "brand": B.brand = v; B.q = ""; renderB(); break;
    case "model": { const m = MODELS[B.cat].find(x => x.id === v); if (m) chooseModel(m); break; }
    case "other": B.other = true; renderB(); { const i = $("bOther"); if (i) i.focus(); } break;
    case "useother": { const i = $("bOther"), n = i && i.value.trim(); if (n) chooseModel(customModel(n)); else if (i) i.focus(); break; }
    case "useq": if (B.q.trim()) chooseModel(customModel(B.q.trim())); break;
    case "rep": if (B.step === 3) toggleSel(v); else { addSel(v); B.hoverKey = null; goB(4); } break;
    case "next": if (B.sel.length) { B.hoverKey = null; goB(4); } break;
    case "all": B.showAll = !B.showAll; renderB(); break;
    case "rm": B.sel.splice(+b.dataset.i, 1); B.sel.length ? renderB() : goB(3, "b"); break;
    case "tier": { const d = B.sel.find(s => CAT.rep[s.key] && CAT.rep[s.key].tiers); if (d) d.tier = v; renderB(); break; }
    case "add": goB(3, "b"); break;
    case "cb": B.act = B.act === "cb" ? null : "cb"; renderB(); if (B.act) { const i = $("cbName"); if (i) i.focus(); } break;
    case "wi": B.act = B.act === "wi" ? null : "wi"; renderB(); break;
    case "wa": { const m = B.model, tt = totalOf(m, B.sel);
      beacon("whatsapp", { category:m.cat, model_id:m.custom ? null : +m.id, device:fullName(m), repairs:repData(m, B.sel), repairs_text:bRepText(), total:tt.text, total_amount:tt.sum }); break; }
    case "restart": Object.assign(B, { step:1, cat:null, model:null, sel:[], done:null, act:null }); renderB("b"); break;
  }
});
$("bldBack").addEventListener("click", () => { if (B.step > 1) goB(B.step - 1, "b"); });
$("bld").addEventListener("input", e => {
  if (e.target.id === "bSearch") { B.q = e.target.value; $("bModels").innerHTML = modelList(); $("bld").querySelectorAll(".brands button").forEach(x => x.setAttribute("aria-pressed", !B.q && x.dataset.v === B.brand)); }
  if (e.target.id === "cbName") B.name = e.target.value;
  if (e.target.id === "cbPhone") B.phone = e.target.value;
});
$("bld").addEventListener("keydown", e => {
  if (e.key === "Escape") closeBuilder();
  if (e.key === "Enter" && e.target.id === "bSearch") { e.preventDefault(); const f = $("bModels").querySelector("[data-b=model],[data-b=useq]"); if (f) f.click(); }
  if (e.key === "Enter" && e.target.id === "bOther") { e.preventDefault(); const n = e.target.value.trim(); if (n) chooseModel(customModel(n)); }
  if (e.key === "Tab") {
    const f = [...$("bldPanel").querySelectorAll("button:not([disabled]),a[href],input,[tabindex]:not([tabindex='-1'])")].filter(x => x.offsetParent !== null);
    if (!f.length) return; const first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); } else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }
});
$("bld").addEventListener("submit", async e => {
  if (e.target.id !== "cbForm") return; e.preventDefault();
  const n = B.name.trim(), p = B.phone.trim(), err = $("cbErr");
  if (!n) { err.textContent = t("err_name"); $("cbName").focus(); return; }
  if (p.replace(/\D/g, "").length < 6) { err.textContent = t("err_phone"); $("cbPhone").focus(); return; }
  const btn = e.target.querySelector("button[type=submit]"); btn.disabled = true; btn.textContent = t("sending"); err.textContent = "";
  const m = B.model, tt = totalOf(m, B.sel);
  try {
    await send("callback", { name:n, phone:p, website:$("cbWeb").value, category:m.cat, model_id:m.custom ? null : +m.id, device:fullName(m),
      repairs:repData(m, B.sel), repairs_text:bRepText(), total:tt.text, total_amount:tt.sum });
    B.done = n; renderB("f");
  } catch (er) {
    err.textContent = er.data && er.data.field === "phone" ? t("err_phone") : er.data && er.data.field === "name" ? t("err_name") : sendErr(er);
    btn.disabled = false; btn.textContent = t("cb_send");
  }
});
let hk = null;
$("bldBody").addEventListener("mouseover", e => {
  const el = e.target.closest("[data-hk],[data-bcat]"); const key = el ? (el.dataset.hk || el.dataset.bcat) : null;
  if (key === hk) return; hk = key; B.hoverKey = key; renderSide();
});
$("bldBody").addEventListener("mouseleave", () => { hk = null; B.hoverKey = null; renderSide(); });

/* ===== Smart describe (hero) ===== */
async function runAsk(text) {
  if (!text.trim()) return;
  try { await loadCatalog(); } catch (e) { $("askMsg").textContent = t("err_send"); return; }
  const r = parse(text);
  if (!r.m && !r.cat && !r.keys.length) { $("askMsg").textContent = t("ai_none"); return; }
  $("askMsg").textContent = "";
  const keys = r.keys;
  if (r.m) {
    const valid = keys.filter(k => k === "diagnosis" || servicesFor(r.m).includes(k));
    openBuilder({ model:r.m, cat:r.m.cat, sel:valid.map(k => CAT.rep[k] && CAT.rep[k].tiers ? { key:k, tier:"p" } : { key:k }) });
  } else openBuilder({ cat:r.cat || null, brand:r.brand || "all", pending:keys });
}
function askMatches(text) {
  // Repair words ("Akku", "Display kaputt") are left out when matching model names.
  const q = norm(text).trim().split(" ").filter(w => !ASK_SKIP.has(w)).join(" "); if (q.length < 2) return [];
  const qq = q.replace(/\s/g, ""), words = q.split(" ").filter(w => w.length > 1), r = parse(text), out = [];
  const all = CATS.flatMap(c => MODELS[c]);
  const push = m => { if (m && !out.includes(m) && out.length < 6) out.push(m); };
  push(r.m);
  for (const a of ALIASES) if (a.a.startsWith(q) || a.a.replace(/\s/g, "").startsWith(qq)) push(a.m);
  for (const m of all) { const n = norm(m.brand + " " + m.name); if (n.includes(" " + q) || n.replace(/\s/g, "").includes(qq)) push(m); }
  if (out.length < 6 && words.length > 1) for (const m of all) { const n = norm(m.brand + " " + m.name); if (words.every(w => n.includes(" " + w) || n.replace(/\s/g, "").includes(w))) push(m); }
  return out.map(m => ({ m, keys:r.keys }));
}
const ASK_SKIP = new Set([...KW.flatMap(([, ws]) => ws.flatMap(w => w.split(" "))), "kaputt", "defekt", "broken", "reparatur", "repair", "wechseln", "tauschen", "austausch", "neu", "new", "mein", "meine", "my", "ist", "is", "geht", "nicht"].filter(w => !/^(pro|max|plus|mini|air|ultra|lite|fe|note|edge|fold|flip)$/.test(w)));
const ASK = { items:[], i:-1 };
function askClose() { const l = $("askList"), i = $("askIn"); if (!l) return; l.hidden = true; i.setAttribute("aria-expanded", "false"); i.removeAttribute("aria-activedescendant"); }
function askRender() {
  const inp = $("askIn"), list = $("askList"); if (!inp || !list) return;
  if (!CAT) { loadCatalog().then(askRender, () => {}); return; }
  ASK.items = askMatches(inp.value); ASK.i = -1;
  if (!ASK.items.length) { askClose(); return; }
  list.innerHTML = ASK.items.map(({ m, keys }, i) => { const k = keys.find(x => servicesFor(m).includes(x)) || "display";
    const kk = servicesFor(m).includes(k) ? k : servicesFor(m)[0];
    return `<li role="option" id="askO${i}" data-i="${i}" aria-selected="false"><span class="ao-n"><small>${esc(t("cat_" + m.cat))}</small><b>${esc(fullName(m))}</b></span><span class="ao-p">${esc(svName(kk, m.cat))}<b>${esc(priceLabel(m, kk))}</b></span></li>`; }).join("");
  list.hidden = false; inp.setAttribute("aria-expanded", "true"); inp.removeAttribute("aria-activedescendant");
}
function askPick(i) {
  const it = ASK.items[i]; if (!it) return;
  const valid = it.keys.filter(k => k === "diagnosis" || servicesFor(it.m).includes(k));
  askClose();
  openBuilder({ model:it.m, cat:it.m.cat, sel:valid.map(k => CAT.rep[k] && CAT.rep[k].tiers ? { key:k, tier:"p" } : { key:k }) });
}
function askMove(d) {
  if ($("askList").hidden || !ASK.items.length) return;
  ASK.i = (ASK.i + d + ASK.items.length) % ASK.items.length;
  $("askList").querySelectorAll("li").forEach((li, i) => li.setAttribute("aria-selected", i === ASK.i));
  $("askIn").setAttribute("aria-activedescendant", "askO" + ASK.i);
}
on("askIn", "input", askRender);
on("askIn", "keydown", e => {
  if (e.key === "ArrowDown") { e.preventDefault(); askMove(1); }
  else if (e.key === "ArrowUp") { e.preventDefault(); askMove(-1); }
  else if (e.key === "Escape" && !$("askList").hidden) { e.stopPropagation(); askClose(); }
});
on("askIn", "blur", () => setTimeout(askClose, 150));
on("askList", "mousedown", e => e.preventDefault());
on("askList", "click", e => { const li = e.target.closest("li[data-i]"); if (li) askPick(+li.dataset.i); });
on("askForm", "submit", e => { e.preventDefault(); if (ASK.i >= 0 && !$("askList").hidden) askPick(ASK.i); else { askClose(); runAsk($("askIn").value); } });
on("askMic", "click", () => voiceGate($("askMic"), (txt, fin) => { $("askIn").value = txt; if (fin) runAsk(txt); }, msg => { $("askMsg").textContent = msg; }));

/* ===== Hero film: desktop and laptop only (wide screen with mouse or trackpad), muted, paused when scrolled away ===== */
const HV_MQ = matchMedia("(min-width:901px) and (hover:hover) and (pointer:fine)");
let HV = null, HV_FAIL = false;
const SND_OFF = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 5 6 9H3v6h3l5 4z"/><path d="m22 9-6 6M16 9l6 6"/></svg>';
const SND_ON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 5 6 9H3v6h3l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M18.8 5.2a9.5 9.5 0 0 1 0 13.6"/></svg>';
function heroVideoOk() {
  const hm = $("heroMedia");
  return !!(hm && hm.dataset.video) && !HV_FAIL && HV_MQ.matches && !reduce && !(navigator.connection && navigator.connection.saveData);
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
  HV = { v, b, on:false, seen:true };
  v.addEventListener("playing", () => v.classList.add("on"));
  v.addEventListener("error", () => { HV_FAIL = true; v.remove(); b.remove(); $("heroMedia").classList.remove("has-vid"); HV = null; });
  b.addEventListener("click", () => { v.muted = !v.muted; if (!v.muted) v.play().catch(() => {}); heroSndLabel(); });
  const start = () => { if (!HV) return; v.src = $("heroMedia").dataset.video; HV.on = true; if (HV.seen && HV_MQ.matches) v.play().catch(() => {}); };
  if (document.readyState === "complete") setTimeout(start, 400); else addEventListener("load", () => setTimeout(start, 400), { once:true });
  if ("IntersectionObserver" in window) new IntersectionObserver(es => {
    if (!HV) return; HV.seen = es[0].isIntersecting; if (!HV.on) return;
    if (HV.seen && HV_MQ.matches) HV.v.play().catch(() => {}); else HV.v.pause();
  }, { threshold:.15 }).observe($("heroMedia"));
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
heroVideo();
HV_MQ.addEventListener("change", e => { if (e.matches && !HV) heroVideo(); });

/* ===== Home sections ===== */
const SELL = { cat:"phone", cond:1, photos:[], n:"", p:"", done:null };
const SP_MAX = 6;
/* Photos are shrunk in the browser (longest side 1600 px, JPEG) and sent as multipart. The server re-encodes them
   without EXIF/GPS, stores them privately and deletes them after 30 days unless a purchase follows. */
function spShrink(file, max = 1600, q = .82) {
  return new Promise(res => {
    const url = URL.createObjectURL(file), im = new Image();
    im.onload = () => { const k = Math.min(1, max / Math.max(im.width, im.height)), c = document.createElement("canvas");
      c.width = Math.round(im.width * k); c.height = Math.round(im.height * k); c.getContext("2d").drawImage(im, 0, 0, c.width, c.height);
      URL.revokeObjectURL(url); c.toBlob(b => res(b ? { blob:b, url:URL.createObjectURL(b) } : null), "image/jpeg", q); };
    im.onerror = () => { URL.revokeObjectURL(url); res(null); };
    im.src = url;
  });
}
async function spAdd(files) {
  const room = SP_MAX - SELL.photos.length; let skipped = 0;
  for (const f of [...files].slice(0, Math.max(0, room))) {
    if (!/^image\//.test(f.type) && !/\.(heic|heif|jpe?g|png|webp)$/i.test(f.name)) { skipped++; continue; }
    const d = await spShrink(f); if (d) SELL.photos.push(d); else skipped++;
  }
  if (files.length > room) toast(t("sp_max", { n:SP_MAX })); else if (skipped) toast(t("sp_bad"));
}
function renderSellPhotos() {
  const box = $("sellPh"); if (!box) return;
  const n = SELL.photos.length, full = n >= SP_MAX;
  $("spRow").innerHTML = SELL.photos.map((d, i) => `<span class="sp-th"><img src="${d.url}" alt="${esc(t("sp_alt", { n:i + 1 }))}"><button type="button" class="sp-rm" data-sprm="${i}" aria-label="${esc(t("sp_rm", { n:i + 1 }))}">${ic("x", 2.4)}</button></span>`).join("") +
    (full ? "" : `<button type="button" class="sp-add sp-cam" data-sp="cam">${ic("camera", 1.8)}<span>${esc(t("sp_cam"))}</span></button><button type="button" class="sp-add" data-sp="lib">${ic("img", 1.8)}<span>${esc(t(n ? "sp_more" : "sp_lib"))}</span></button>`);
  if (SELL.done) {
    $("spSend").innerHTML = `<div class="sp-ok" tabindex="-1" id="spOk"><span class="ck">${ic("check", 2.4)}</span><div><b>${esc(t("sp_done_t", { n:SELL.done }))}</b><p>${esc(t("sp_done"))}</p></div></div>`;
    box.hidden = true; $("sellWa").hidden = true; return;
  }
  box.hidden = false; $("sellWa").hidden = false;
  $("sellWa").classList.toggle("alt", n > 0);
  $("sellWa").querySelector("span").textContent = t(n ? "sell_btn_alt" : "sell_btn");
  $("spSend").innerHTML = n ? `<div class="two"><div><label class="lab-l" for="spName">${esc(t("name_l"))}</label><input class="inp" id="spName" autocomplete="name" value="${esc(SELL.n)}"></div><div><label class="lab-l" for="spPhone">${esc(t("sp_phone"))}</label><input class="inp" id="spPhone" type="tel" autocomplete="tel" value="${esc(SELL.p)}"></div></div>
    <p class="err" id="spErr" role="alert"></p><button type="submit" class="btn sp-go">${ic("check", 2.4)}${esc(t("sp_send", { n }))}</button>` : "";
}
function updSell() {
  const wa = $("sellWa"); if (!wa) return;
  const model = $("sellModel").value.trim();
  wa.href = waLink(t("wa_sell", { c:t("cat_" + SELL.cat), m:model || "?", k:t("conds")[SELL.cond] }));
  $("sellCat").querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", b.dataset.v === SELL.cat));
  $("sellCond").querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", +b.dataset.v === SELL.cond));
  const g = $("sellGuide");
  if (g) {
    g.textContent = "";
    if (model && CAT && CAT.buy) {
      const r = parse(model), m = r.m && r.m.cat === SELL.cat ? r.m : null, row = m && CAT.buy[m.id] && CAT.buy[m.id][SELL.cond];
      if (row) g.textContent = t("guide", { m:fullName(m), p:fmt(row[0]) + "–" + fmt(row[1]) });
    }
  }
}
on("sellCat", "click", e => { const b = e.target.closest("button"); if (!b) return; SELL.cat = b.dataset.v; updSell(); });
on("sellCond", "click", e => { const b = e.target.closest("button"); if (!b) return; SELL.cond = +b.dataset.v; updSell(); });
on("sellModel", "input", () => { updSell(); if (!CAT) loadCatalog().then(updSell, () => {}); });
on("sellForm", "click", e => {
  const a = e.target.closest("[data-sp]"); if (a) { $(a.dataset.sp === "cam" ? "spCam" : "spLib").click(); return; }
  const r = e.target.closest("[data-sprm]");
  if (r) { const [d] = SELL.photos.splice(+r.dataset.sprm, 1); if (d) URL.revokeObjectURL(d.url); renderSellPhotos(); const nx = $("spRow").querySelector("button"); if (nx) nx.focus(); }
});
["spCam", "spLib"].forEach(id => on(id, "change", e => { const fs = e.target.files; if (fs && fs.length) spAdd(fs).then(renderSellPhotos); e.target.value = ""; }));
on("sellForm", "input", e => { if (e.target.id === "spName") SELL.n = e.target.value; if (e.target.id === "spPhone") SELL.p = e.target.value; });
on("sellForm", "submit", async e => {
  e.preventDefault(); if (!SELL.photos.length) return;
  const n = SELL.n.trim(), p = SELL.p.trim(), err = $("spErr");
  if (!n) { err.textContent = t("err_name"); $("spName").focus(); return; }
  if (p.replace(/\D/g, "").length < 6) { err.textContent = t("err_phone"); $("spPhone").focus(); return; }
  const btn = e.target.querySelector("button[type=submit]"), label = btn.innerHTML; btn.disabled = true; btn.textContent = t("sending"); err.textContent = "";
  const model = $("sellModel").value.trim(), r = CAT && model ? parse(model) : {};
  const fd = new FormData();
  const fields = { kind:"offer", lang, source:location.pathname, ts:D.ts, name:n, phone:p, website:$("spWeb").value, category:SELL.cat,
    device:(t("cat_" + SELL.cat) + " " + model).trim(), model_id:r.m && r.m.cat === SELL.cat ? r.m.id : "", condition:t("conds")[SELL.cond],
    repairs_text:t("sp_req", { k:t("conds")[SELL.cond] }) };
  for (const k in fields) fd.append(k, fields[k]);
  SELL.photos.forEach((d, i) => fd.append("photos", d.blob, `foto-${i + 1}.jpg`));
  try {
    const res = await fetch(D.api.request, { method:"POST", credentials:"same-origin", headers:{ "Accept":"application/json", "X-CSRFToken":csrf() }, body:fd });
    let j = {}; try { j = await res.json(); } catch (x) {}
    if (!res.ok) { const er = new Error(j.error || "send"); er.status = res.status; er.data = j; throw er; }
    SELL.photos.forEach(d => URL.revokeObjectURL(d.url));
    SELL.done = n; SELL.photos = []; SELL.n = SELL.p = ""; renderSellPhotos(); $("spOk").focus();
  } catch (er) {
    err.textContent = er.data && er.data.field === "phone" ? t("err_phone") : er.data && er.data.field === "name" ? t("err_name") : er.data && er.data.field === "photos" ? t("sp_bad") : sendErr(er);
    btn.disabled = false; btn.innerHTML = label;
  }
});
renderSellPhotos();
on("sellWa", "click", () => beacon("sale", { category:SELL.cat, device:$("sellModel").value.trim(), condition:t("conds")[SELL.cond] }));
on("copyAddr", "click", () => copyText(D.mailin, t("copied")));
document.querySelectorAll('[data-wa="ask"]').forEach(a => a.addEventListener("click", () => beacon("whatsapp", { repairs_text:t("ways")[1][0] })));

on("brandWall", "click", e => { const b = e.target.closest("[data-bc]"); if (b) openBuilder({ cat:b.dataset.bc, brand:b.dataset.bb }); });
on("heroDevs", "click", e => { const b = e.target.closest("[data-hcat]"); if (b) openBuilder({ cat:b.dataset.hcat }); });
on("rail", "click", e => { const b = e.target.closest("[data-rail]"); if (b) openBuilder({ cat:"phone", pending:[b.dataset.rail] }); });
on("labTrack", "click", e => { const b = e.target.closest("[data-lab]"); if (b) openBuilder({ pending:[b.dataset.lab] }); });
document.addEventListener("click", e => {
  const b = e.target.closest("[data-open-builder]"); if (!b) return;
  e.preventDefault();
  const o = {};
  if (b.dataset.model) { const go = () => { const m = CATS.flatMap(c => MODELS[c]).find(x => x.slug === b.dataset.model); if (m) { o.model = m; if (b.dataset.repair) o.sel = b.dataset.repair.split(",").filter(k => k === "diagnosis" || servicesFor(m).includes(k)).map(k => CAT.rep[k].tiers ? { key:k, tier:b.dataset.tier === "o" ? "o" : "p" } : { key:k }); } openBuilder(o); };
    CAT ? go() : loadCatalog().then(go, () => toast(t("err_send"))); return; }
  if (b.dataset.cat) o.cat = b.dataset.cat;
  openBuilder(o);
});

/* Before / after */
(function () {
  const cmp = $("cmp"); if (!cmp) return; let drag = false;
  const set = x => { x = Math.max(0, Math.min(100, x)); cmp.style.setProperty("--x", x + "%"); const k = cmp.querySelector(".knob"); if (k) k.setAttribute("aria-valuenow", Math.round(x)); cmp.dataset.x = x; };
  const at = ev => { const r = cmp.getBoundingClientRect(); set((ev.clientX - r.left) / r.width * 100); };
  cmpSet = set;
  cmp.addEventListener("pointerdown", ev => { cmp.dataset.touched = "1"; drag = true; cmp.setPointerCapture(ev.pointerId); at(ev); });
  cmp.addEventListener("pointermove", ev => { if (drag) at(ev); });
  cmp.addEventListener("pointerup", () => { drag = false; });
  cmp.addEventListener("keydown", ev => {
    cmp.dataset.touched = "1"; const x = +(cmp.dataset.x || 50);
    if (ev.key === "ArrowLeft" || ev.key === "ArrowDown") { set(x - 5); ev.preventDefault(); }
    if (ev.key === "ArrowRight" || ev.key === "ArrowUp") { set(x + 5); ev.preventDefault(); }
    if (ev.key === "Home") { set(0); ev.preventDefault(); } if (ev.key === "End") { set(100); ev.preventDefault(); }
  });
})();

/* ===== Motion: reveals, stickers, drawers, count-up, slider sweep, tile tilt, nav ===== */
const io = ANIM && "IntersectionObserver" in window ? new IntersectionObserver(ents => {
  ents.forEach(en => {
    if (!en.isIntersecting) return;
    const el = en.target; io.unobserve(el);
    if (el.classList.contains("wait")) { el.classList.remove("wait"); el.classList.add("on"); }
    else el.classList.add("in");
    el.querySelectorAll(":scope > .wipe").forEach(w => w.classList.add("in"));
    if (el.dataset.count) countUp(el);
    if (el.id === "cmp") sweep();
  });
}, { threshold:.2, rootMargin:"0px 0px -6% 0px" }) : null;
function watch(root = document) {
  if (!root) return;
  root.querySelectorAll(".wipe:not(.seen)").forEach(w => {
    w.classList.add("seen"); const host = w.parentElement;
    if (io) io.observe(host); else w.classList.add("in");
  });
  root.querySelectorAll("[data-rv]:not(.seen), .stk.wait:not(.seen), .drw.wait:not(.seen), [data-count]:not(.seen), #cmp:not(.seen)").forEach(el => {
    el.classList.add("seen");
    if (io) io.observe(el); else { el.classList.remove("wait"); el.classList.add("in", "on"); }
  });
}
function countUp(el) {
  const to = +el.dataset.count, nf = new Intl.NumberFormat(lang === "de" ? "de-DE" : "en-IE"), t0 = performance.now(), dur = 1600;
  const step = now => { const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 3); el.textContent = nf.format(Math.round(to * e / 10) * 10); if (k < 1) requestAnimationFrame(step); };
  requestAnimationFrame(step);
}
let swept = false;
function sweep() {
  if (swept || !ANIM) return; swept = true;
  const cmp = $("cmp"), pts = [[0, 50], [750, 80], [1650, 18], [2400, 50]];
  const ease = x => x < .5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2;
  let t0 = null;
  const frame = ts => {
    if (cmp.dataset.touched) return;
    if (t0 == null) t0 = ts;
    const e = ts - t0, i = pts.findIndex(p => p[0] > e);
    if (i === -1) { cmpSet(50); return; }
    const [a0, v0] = pts[i - 1], [a1, v1] = pts[i];
    cmpSet(v0 + (v1 - v0) * ease((e - a0) / (a1 - a0)));
    requestAnimationFrame(frame);
  };
  setTimeout(() => requestAnimationFrame(frame), 350);
}
function tilt(box) {
  if (!box || !ANIM || !matchMedia("(pointer:fine)").matches) return;
  box.addEventListener("pointermove", e => {
    const d = e.target.closest(".dev"); if (!d || !box.contains(d)) return;
    const r = d.querySelector(".tile").getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)), y = Math.max(0, Math.min(1, (e.clientY - r.top) / r.height));
    d.classList.add("tilting");
    d.style.setProperty("--ry", ((x - .5) * 16).toFixed(2) + "deg");
    d.style.setProperty("--rx", ((.5 - y) * 16).toFixed(2) + "deg");
    d.style.setProperty("--gx", (x * 100).toFixed(1) + "%");
    d.style.setProperty("--gy", (y * 100).toFixed(1) + "%");
  });
  box.addEventListener("pointerout", e => {
    const d = e.target.closest(".dev"); if (!d || d.contains(e.relatedTarget)) return;
    d.classList.remove("tilting"); d.style.setProperty("--rx", "0deg"); d.style.setProperty("--ry", "0deg");
  });
}
tilt($("heroDevs")); tilt($("bldBody"));
(function () {
  const nav = document.querySelector(".nav"); let last = scrollY, tick = false;
  const upd = () => {
    const y = scrollY, h = document.documentElement.scrollHeight - innerHeight;
    nav.classList.toggle("scrolled", y > 8);
    if (ANIM && !document.documentElement.classList.contains("menu-open")) { if (y > last + 4 && y > 320) nav.classList.add("hide"); else if (y < last - 4 || y < 320) nav.classList.remove("hide"); }
    nav.style.setProperty("--p", h > 0 ? (y / h).toFixed(4) : 0);
    last = y; tick = false;
  };
  addEventListener("scroll", () => { if (!tick) { tick = true; requestAnimationFrame(upd); } }, { passive:true });
  nav.addEventListener("focusin", () => nav.classList.remove("hide"));
  upd();
})();
(function () {
  const btn = $("menuBtn"), pnl = $("mnav"); if (!btn || !pnl) return;
  const set = o => {
    btn.setAttribute("aria-expanded", o); pnl.hidden = !o;
    document.documentElement.classList.toggle("menu-open", o);
    if (o) document.querySelector(".nav").classList.remove("hide");
  };
  btn.addEventListener("click", () => set(btn.getAttribute("aria-expanded") !== "true"));
  pnl.addEventListener("click", e => { if (e.target.closest("a")) set(false); });
  addEventListener("keydown", e => { if (e.key === "Escape" && !pnl.hidden) { set(false); btn.focus(); } });
  matchMedia("(min-width:901px)").addEventListener("change", e => { if (e.matches) set(false); });
})();
/* language switch: remember the choice (necessary cookie tt-lang, see cookie policy) */
document.querySelectorAll(".lang a[data-lang], a.lang-sw[data-lang]").forEach(a => a.addEventListener("click", () => {
  document.cookie = "tt-lang=" + a.dataset.lang + "; Max-Age=31536000; Path=/; SameSite=Lax" + (location.protocol === "https:" ? "; Secure" : "");
}));

/* ===== Repair request page (/anfrage) ===== */
(function () {
  const f = $("leadForm"); if (!f) return;
  const LEAD = { cat:f.elements.category.value || "phone", where:+f.elements.method_i.value || 0, via:+f.elements.via_i.value || 0 };
  const seg = (id, key, field) => on(id, "click", e => {
    const x = e.target.closest("button"); if (!x) return;
    LEAD[key] = key === "cat" ? x.dataset.v : +x.dataset.v;
    $(id).querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", b === x));
    f.elements[field].value = x.dataset.v;
    if (key === "cat") fillModels();
    hint();
  });
  function fillModels() {
    const dl = $("lfModels"); if (!dl || !CAT) return;
    dl.innerHTML = (MODELS[LEAD.cat] || []).map(m => `<option value="${esc(fullName(m))}">`).join("");
  }
  seg("lfCat", "cat", "category"); seg("lfWhere", "where", "method_i"); seg("lfVia", "via", "via_i");
  const hint = () => {
    const el = $("lfHint"); if (!CAT) return;
    const txt = ($("lfModel").value + " " + $("lfProb").value).trim(); if (!txt) { el.textContent = ""; return; }
    const r = parse(txt), bits = [];
    if (r.m) bits.push(fullName(r.m)); else if (r.cat) bits.push(t("cat_" + r.cat));
    if (r.keys.length) bits.push(r.keys.map(k => svName(k, r.m ? r.m.cat : r.cat)).join(", "));
    if (r.m && r.keys.length) { const v = r.keys.filter(k => k === "diagnosis" || servicesFor(r.m).includes(k)).map(k => ({ key:k, tier:CAT.rep[k] && CAT.rep[k].tiers ? "p" : undefined })); if (v.length) bits.push(totalOf(r.m, v).text); }
    el.textContent = bits.length ? t("lf_hint", { x:bits.join(" · ") }) : "";
  };
  loadCatalog().then(() => { fillModels(); hint(); }, () => {});
  on("lfProb", "input", hint); on("lfModel", "input", hint);
  on("lfMic", "click", () => voiceGate($("lfMic"), txt => { $("lfProb").value = txt; hint(); }, msg => { $("lfHint").textContent = msg; }));
  f.addEventListener("submit", async e => {
    e.preventDefault();
    const n = $("lfName").value.trim(), p = $("lfPhone").value.trim(), err = $("lfErr");
    if (!n) { err.textContent = t("err_name"); $("lfName").focus(); return; }
    if (p.replace(/\D/g, "").length < 6) { err.textContent = t("err_phone"); $("lfPhone").focus(); return; }
    const btn = f.querySelector("button[type=submit]"), label = btn.textContent; btn.disabled = true; btn.textContent = t("sending"); err.textContent = "";
    const model = $("lfModel").value.trim(), r = CAT ? parse(model) : {};
    try {
      await send("form", { name:n, phone:p, website:f.elements.website.value, category:LEAD.cat, device:model || t("cat_" + LEAD.cat),
        model_id:r.m ? +r.m.id : null,
        problem:$("lfProb").value.trim(), method:["moabit", "mailin"][LEAD.where] || "moabit", contact_via:["whatsapp", "phone"][LEAD.via] });
      $("leadBody").innerHTML = `<div class="form-card"><div class="ok" tabindex="-1" id="lfOk"><span class="ck">${ic("check", 2.4)}</span><h2 class="bt">${esc(t("cb_done_t", { n }))}</h2><p class="bs">${esc(t("lf_done", { n, v:t("vias")[LEAD.via] }))}</p><a class="btn" href="${location.pathname}">${esc(t("lf_new"))}</a></div></div>`;
      $("lfOk").focus();
    } catch (er) {
      err.textContent = er.data && er.data.field === "phone" ? t("err_phone") : er.data && er.data.field === "name" ? t("err_name") : sendErr(er);
      btn.disabled = false; btn.textContent = label;
    }
  });
  const q = new URLSearchParams(location.search).get("q"); if (q && !$("lfProb").value) { $("lfProb").value = q; }
})();

/* ===== Electronic withdrawal function (§ 356a BGB): step 1 opens the form, step 2 "Widerruf bestätigen" sends it ===== */
(function () {
  const box = $("wd"); if (!box) return;
  document.addEventListener("click", e => {
    const w = e.target.closest("[data-wd=open]"); if (!w) return;
    e.preventDefault(); $("wdStart").hidden = true; $("wdForm").hidden = false; $("wdN").focus();
  });
  const f = $("wdForm"); if (!f) return;
  f.addEventListener("submit", async e => {
    e.preventDefault();
    const err = $("wdErr"), n = $("wdN").value.trim(), m = $("wdM").value.trim(), r = $("wdR").value.trim();
    if (!n) { err.textContent = t("wd_err_name"); $("wdN").focus(); return; }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(m)) { err.textContent = t("wd_err_mail"); $("wdM").focus(); return; }
    if (!r) { err.textContent = t("wd_err_ref"); $("wdR").focus(); return; }
    const btn = f.querySelector("button[type=submit]"), label = btn.textContent; btn.disabled = true; btn.textContent = t("sending"); err.textContent = "";
    try {
      const j = await send("withdrawal", { name:n, email:m, reference:r, device:$("wdD").value.trim(), message:$("wdX").value.trim(), website:f.elements.website.value });
      const at = new Date(j.received_at), dt = o => new Intl.DateTimeFormat(lang === "de" ? "de-DE" : "en-GB", Object.assign({ timeZone:"Europe/Berlin" }, o)).format(at);
      const d = j.withdrawal || {};
      box.outerHTML = `<div class="wd done" id="wd" tabindex="-1"><span class="ck">${ic("check", 2.4)}</span><h2>${esc(t("wd_done_h"))}</h2>
        <p>${esc(t("wd_done_p", { d:dt({ dateStyle:"long" }), t:dt({ timeStyle:"short" }), m }))}</p>
        ${j.mail_ok === false ? `<p class="fine">${esc(t("wd_mail_err"))}</p>` : ""}
        <dl class="wd-sum"><dt>${esc(t("wd_s_n"))}</dt><dd>${esc(n)}</dd><dt>${esc(t("wd_s_r"))}</dt><dd>${esc(r)}</dd>${d.device ? `<dt>${esc(t("wd_s_d"))}</dt><dd>${esc(d.device)}</dd>` : ""}${d.message ? `<dt>${esc(t("wd_s_x"))}</dt><dd>${esc(d.message)}</dd>` : ""}</dl>
        <a class="btn line" href="${URLS.withdraw}">${esc(t("wd_new"))}</a></div>`;
      const nb = $("wd"); nb.focus({ preventScroll:true }); nb.scrollIntoView({ block:"center" });
    } catch (er) {
      err.textContent = sendErr(er); btn.disabled = false; btn.textContent = label;
    }
  });
  if (location.pathname === URLS.withdraw) requestAnimationFrame(() => { const w = $("wd"), n = $("wdN"); if (w) w.scrollIntoView({ block:"center", behavior:"instant" }); if (n && !$("wdForm").hidden) n.focus({ preventScroll:true }); });
})();

/* legal pages: table of contents scrolls and focuses the section */
document.addEventListener("click", e => {
  const to = e.target.closest("[data-lgto]"); if (!to) return;
  const el = document.getElementById(to.dataset.lgto); if (!el) return;
  e.preventDefault(); el.scrollIntoView({ behavior:reduce ? "auto" : "smooth", block:"start" }); el.setAttribute("tabindex", "-1"); el.focus({ preventScroll:true });
});
(function () { const nv = document.querySelector(".lg-nav"), cur = nv && nv.querySelector("[aria-current]"); if (cur && nv.scrollWidth > nv.clientWidth) nv.scrollLeft = cur.offsetLeft - (nv.clientWidth - cur.offsetWidth) / 2; })();

/* ---------- Cookie consent (§ 25 TDDDG, DSK guidance: reject as easy as accept, on the first layer) ---------- */
const CONSENT_V = (D.consent && D.consent.v) || 1, CC_CATS = (D.consent && D.consent.cats) || ["necessary"], CC_MAX_AGE = 365 * 864e5;
const COOKIES = D.cookies || {};
let consent = LS.get("tt-consent", null);
if (consent && (consent.v !== CONSENT_V || !(Date.now() - Date.parse(consent.ts) < CC_MAX_AGE))) consent = null;
// Optional services register their loader here. Nothing in it runs before consent.
const CC_LOADERS = { stats:[], marketing:[] };
if (D.matomo && D.matomo.url) CC_LOADERS.stats.push(() => {
  const u = D.matomo.url.replace(/\/?$/, "/"), _paq = window._paq = window._paq || [];
  _paq.push(["setTrackerUrl", u + "matomo.php"], ["setSiteId", D.matomo.site], ["trackPageView"], ["enableLinkTracking"]);
  const s = document.createElement("script"); s.async = true; s.src = u + "matomo.js"; document.head.appendChild(s);
});
if (D.ads && D.ads.gads) CC_LOADERS.marketing.push(() => {
  window.dataLayer = window.dataLayer || []; window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag("js", new Date()); window.gtag("config", D.ads.gads);
  const s = document.createElement("script"); s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(D.ads.gads); document.head.appendChild(s);
});
const ccLoaded = {};
const ccId = () => { try { return crypto.randomUUID().slice(0, 8); } catch (e) { return Math.random().toString(36).slice(2, 10); } };
function ccClear(k) {
  const re = k === "stats" ? /^_pk_/ : /^(_gcl_|_fbp|_ga)/;
  const host = location.hostname.replace(/^www\./, "");
  document.cookie.split(";").map(c => c.split("=")[0].trim()).filter(n => re.test(n)).forEach(n => {
    document.cookie = n + "=; Max-Age=0; path=/";
    if (host) document.cookie = n + "=; Max-Age=0; path=/; domain=." + host;
  });
}
function ccApply() {
  ["stats", "marketing"].forEach(k => {
    if (consent && consent[k] && CC_CATS.includes(k)) { if (!ccLoaded[k]) { ccLoaded[k] = 1; CC_LOADERS[k].forEach(f => { try { f(); } catch (e) {} }); } }
    else ccClear(k);
  });
  document.documentElement.dataset.consent = consent ? CC_CATS.filter(k => consent[k]).join(" ") : "none";
}
function ccSave(sel, action) {
  consent = { v:CONSENT_V, ts:new Date().toISOString(), id:(consent && consent.id) || ccId(), necessary:true,
    stats:!!sel.stats && CC_CATS.includes("stats"), marketing:!!sel.marketing && CC_CATS.includes("marketing") };
  LS.set("tt-consent", consent);
  try { fetch(D.api.consent, { method:"POST", credentials:"same-origin", keepalive:true, headers:{ "Content-Type":"application/json", "X-CSRFToken":csrf() },
    body:JSON.stringify({ id:consent.id, v:consent.v, ts:consent.ts, action, lang, choices:{ necessary:true, stats:consent.stats, marketing:consent.marketing } }) }).catch(() => {}); } catch (e) {}
  ccApply(); closeCCM(); renderCC(); toast(t("cc_saved"));
  if ($("ccbox")) renderCCBox();
}
function ccPad() { const el = $("cc"); document.documentElement.style.setProperty("--cc-h", (el.hidden ? 0 : el.offsetHeight) + "px"); }
const ccLinks = () => `<p class="cc-l"><a href="${URLS.datenschutz}">${esc(t("f_priv"))}</a><a href="${URLS.cookies}">${esc(t("f_ck"))}</a><a href="${URLS.impressum}">${esc(t("f_imp"))}</a></p>`;
function ccText() {
  const st = CC_CATS.includes("stats"), mk = CC_CATS.includes("marketing");
  return st && mk ? t("cc_p") : st ? t("cc_p_stats") : mk ? t("cc_p_ads") : t("cc_p_min");
}
function renderCC() {
  const show = !consent;
  const el = $("cc");
  el.innerHTML = `<div class="cc-in"><div class="cc-tx"><h2 id="ccH">${esc(t("cc_h"))}</h2><p>${esc(ccText())}</p>
    ${ccLinks()}</div>
    <div class="cc-act"><button type="button" class="ccb" data-cc="reject">${esc(t("cc_rej"))}</button><button type="button" class="ccb" data-cc="accept">${esc(t("cc_acc"))}</button><button type="button" class="cc-set" data-cc="settings">${esc(t("cc_set"))}</button></div></div>`;
  if (show && el.hidden && !el.dataset.seen) { el.dataset.seen = "1"; el.classList.add("intro"); setTimeout(() => el.classList.remove("intro"), 1600); }
  el.hidden = !show;
  document.documentElement.classList.toggle("cc-open", show);
  requestAnimationFrame(ccPad);
  if (!$("ccm").hidden) renderCCM();
}
const dtFmt = (d, o) => { try { return new Intl.DateTimeFormat(lang === "de" ? "de-DE" : "en-GB", Object.assign({ timeZone:"Europe/Berlin" }, o)).format(d); } catch (e) { return d.toISOString(); } };
function renderCCBox() {
  const box = $("ccbox"); if (!box) return;
  const c = consent;
  const row = k => { const on = k === "necessary" || (c && c[k]); return `<li><span>${esc(t("cc_cat")[k][0])}</span><b class="${on ? "on" : "off"}">${esc(k === "necessary" ? t("cc_always") : on ? t("cc_on") : t("cc_off"))}</b></li>`; };
  box.innerHTML = `<h2>${esc(t("cc_state"))}</h2>${c ? `<ul>${CC_CATS.map(row).join("")}</ul><p class="lg-meta">${esc(t("cc_when", { d:dtFmt(new Date(c.ts), { dateStyle:"medium", timeStyle:"short" }) }))}. ${esc(t("cc_id"))}: <code>${esc(c.id)}</code></p>` : `<p>${esc(t("cc_none"))}</p>`}<button type="button" class="btn" data-ccopen>${esc(t("cc_change"))}</button>`;
}
let CCM_SEL = { stats:false, marketing:false }, ccmReturn = null;
function renderCCM() {
  const cat = k => {
    const c = t("cc_cat")[k], list = COOKIES[k] || [], nec = k === "necessary";
    return `<div class="ccat"><div class="ccat-h"><label for="cc_${k}"><b>${esc(c[0])}</b><small>${esc(c[1])}</small></label>${nec ? `<span class="always">${esc(t("cc_always"))}</span>` : ""}<input type="checkbox" role="switch" class="sw" id="cc_${k}"${nec ? " checked disabled" : ` data-cck="${k}"${CCM_SEL[k] ? " checked" : ""}`}></div>
      ${list.length ? `<details><summary>${esc(t("cc_show", { n:list.length }))}</summary><ul class="cclist">${list.map(r => `<li><code>${esc(r[0])}</code><span>${esc(r[1])}</span><span>${esc(r[2])}</span><span>${esc(r[3])}</span></li>`).join("")}</ul></details>` : ""}</div>`;
  };
  $("ccmP").innerHTML = `<div class="ccm-top"><h2 id="ccmH">${esc(t("cc_title"))}</h2><button type="button" class="icb" data-ccx aria-label="${esc(t("close"))}">${ic("x", 2)}</button></div>
    <p class="ccm-intro">${esc(t("cc_intro"))}</p>${CC_CATS.map(cat).join("")}
    ${ccLinks()}
    <div class="ccm-act"><button type="button" class="ccb" data-cc="reject">${esc(t("cc_rej"))}</button><button type="button" class="ccb alt" data-cc="save">${esc(t("cc_save"))}</button><button type="button" class="ccb" data-cc="accept">${esc(t("cc_acc"))}</button></div>`;
}
function lockScroll() { document.documentElement.style.overflow = (!$("bld").hidden || !$("ccm").hidden || !$("micm").hidden) ? "hidden" : ""; }
function openCCM() {
  CCM_SEL = { stats:!!(consent && consent.stats), marketing:!!(consent && consent.marketing) };
  ccmReturn = document.activeElement;
  renderCCM(); $("ccm").hidden = false; lockScroll(); $("ccmP").focus({ preventScroll:true });
}
function closeCCM() {
  if ($("ccm").hidden) return;
  $("ccm").hidden = true; lockScroll();
  if (ccmReturn && ccmReturn.isConnected && ccmReturn.focus) ccmReturn.focus({ preventScroll:true });
}
document.addEventListener("click", e => {
  const b = e.target.closest("[data-cc]");
  if (b) {
    const a = b.dataset.cc;
    if (a === "accept") ccSave({ stats:true, marketing:true }, "accept");
    else if (a === "reject") ccSave({ stats:false, marketing:false }, "reject");
    else if (a === "save") ccSave(CCM_SEL, "save");
    else if (a === "settings") openCCM();
    return;
  }
  if (e.target.closest("[data-ccx]")) return closeCCM();
  if (e.target.closest("[data-ccopen]")) return openCCM();
  if (e.target.closest("[data-micx]")) return closeMic();
  if (e.target.closest("[data-mic-ok]")) { const go = micPending; micPending = null; closeMic(true); if (go) go(); }
});
$("ccm").addEventListener("change", e => { const k = e.target.dataset && e.target.dataset.cck; if (k) CCM_SEL[k] = e.target.checked; });
function trapTab(e, panel) {
  if (e.key !== "Tab") return;
  const f = [...panel.querySelectorAll("button:not([disabled]),a[href],input:not([disabled]),summary,[tabindex]:not([tabindex='-1'])")].filter(x => x.offsetParent !== null);
  if (!f.length) return; const first = f[0], last = f[f.length - 1];
  if (e.shiftKey && (document.activeElement === first || document.activeElement === panel)) { e.preventDefault(); last.focus(); }
  else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
}
$("ccm").addEventListener("keydown", e => trapTab(e, $("ccmP")));
$("micm").addEventListener("keydown", e => trapTab(e, $("micP")));
addEventListener("keydown", e => {
  if (e.key !== "Escape") return;
  if (!$("micm").hidden) closeMic(); else if (!$("ccm").hidden) closeCCM();
});
addEventListener("resize", () => { if (!$("cc").hidden) ccPad(); });

/* ---------- Voice input notice: shown once before the browser's speech recognition is used ---------- */
let micPending = null, micReturn = null;
function voiceGate(btn, onText, say) {
  if (LS.get("tt-mic-ok", false)) return startVoice(btn, onText, say);
  micPending = () => { LS.set("tt-mic-ok", true); startVoice(btn, onText, say); };
  micReturn = btn;
  $("micP").innerHTML = `<div class="ccm-top"><h2 id="micH">${ic("mic")}<span>${esc(t("mic_h"))}</span></h2><button type="button" class="icb" data-micx aria-label="${esc(t("close"))}">${ic("x", 2)}</button></div>
    <p class="ccm-intro">${esc(t("mic_p"))}</p><p class="fine"><a href="${URLS.datenschutz}">${esc(t("f_priv"))}</a></p>
    <div class="ccm-act two-b"><button type="button" class="ccb alt" data-micx>${esc(t("mic_no"))}</button><button type="button" class="ccb" data-mic-ok>${esc(t("mic_ok"))}</button></div>`;
  $("micm").hidden = false; lockScroll(); $("micP").focus({ preventScroll:true });
}
function closeMic(keep) {
  if ($("micm").hidden) return;
  $("micm").hidden = true; lockScroll();
  if (!keep) micPending = null;
  if (micReturn && micReturn.focus) micReturn.focus({ preventScroll:true });
}

/* ===== Boot ===== */
addEventListener("keydown", e => { if (e.key === "Escape" && !$("bld").hidden && $("micm").hidden && $("ccm").hidden) closeBuilder(); });
addEventListener("hashchange", () => { if (readHash()) fromHash(); });
ccApply();
renderCC();
renderCCBox();
hydrate();
watch(document);
updStatus();
setInterval(updStatus, 60000);
if (readHash()) fromHash();
else {
  // prefetch the catalogue once the page has settled, or as soon as the visitor reaches for the calculator
  const pre = () => loadCatalog().catch(() => {});
  addEventListener("load", () => setTimeout(() => ("requestIdleCallback" in window ? requestIdleCallback(pre, { timeout:5000 }) : pre()), 3000), { once:true });
  ["pointerdown", "keydown", "focusin"].forEach(ev => addEventListener(ev, e => { if (e.target.closest && e.target.closest("[data-open-builder],[data-hcat],[data-rail],[data-bc],#askIn,#lfModel,#sellModel")) pre(); }, { passive:true }));
}
})();
