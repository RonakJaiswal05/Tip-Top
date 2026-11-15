/* ===== Services & prices ===== */
const SV = {
  display:["Display","Display Reparatur"], battery:["Battery replacement","Akku Austausch"], port:["Charging port","Ladebuchse Reparatur"],
  back:["Back cover","Backcover Reparatur"], camera:["Rear camera","Kamera Reparatur"], water:["Water damage check","Wasserschaden Diagnose"],
  camglass:["Camera glass","Kameraglas Reparatur"], frontcam:["Front camera","Frontkamera Reparatur"], faceid:["Face ID","Face ID Reparatur"],
  speaker:["Loudspeaker","Lautsprecher Reparatur"], earpiece:["Earpiece","Hörmuschel Reparatur"], mic:["Microphone","Mikrofon Reparatur"],
  mainboard:["Mainboard repair","Mainboard Reparatur"], data:["Data recovery (diagnosis)","Datenrettung (Diagnose)"], software:["Software repair","Software Reparatur"],
  buttons:["Buttons","Tasten Reparatur"], vibration:["Vibration motor","Vibrationsmotor Reparatur"], sim:["SIM card reader","SIM-Kartenleser Reparatur"],
  jack:["Headphone jack","Kopfhörerbuchse Reparatur"], diagnosis:["Fault diagnosis","Fehlerdiagnose"],
  keyboard:["Keyboard","Tastatur Reparatur"], trackpad:["Trackpad","Trackpad Reparatur"], hinge:["Hinge","Scharnier Reparatur"],
  fan:["Fan and cleaning","Lüfter und Reinigung"], ssd:["SSD and upgrade","SSD und Aufrüstung"],
  hdmi:["HDMI port","HDMI-Buchse Reparatur"], drive:["Disc drive","Laufwerk Reparatur"], psu:["Power supply","Netzteil Reparatur"],
  drift:["Stick drift","Stick-Drift Reparatur"], cport:["Controller charging port","Controller-Ladebuchse"]
};
const SV_CAT = {
  tablet:{ back:["Housing and back","Gehäuse und Rückseite"] },
  laptop:{ back:["Housing","Gehäuse Reparatur"], port:["Charging port / DC jack","Ladebuchse / DC-Buchse"], software:["Operating system and software","Betriebssystem und Software"] },
  console:{ display:["Screen (handheld)","Bildschirm (Handheld)"], fan:["Overheating and cleaning","Überhitzung und Reinigung"], software:["Software and firmware","Software und Firmware"], ssd:["Storage upgrade","Speicher-Upgrade"], battery:["Battery","Akku Austausch"] }
};
const svName = (k, cat) => { const o = (SV_CAT[cat] || {})[k] || SV[k] || [k, k]; return o[lang === "de" ? 1 : 0]; };
const ICON_OF = { cport:"port" };

const LISTS = {
  phone:["display","battery","port","back","camera","water","camglass","frontcam","faceid","speaker","earpiece","mic","mainboard","data","software","buttons","vibration","sim","jack"],
  tablet:["display","battery","port","back","camera","water","frontcam","speaker","mic","buttons","mainboard","data","software"],
  laptop:["display","battery","keyboard","port","fan","water","trackpad","hinge","ssd","speaker","mainboard","data","software"]
};
const CON = {
  B:["hdmi","fan","drive","psu","ssd","water","software","mainboard"],
  b:["hdmi","fan","psu","ssd","water","software","mainboard"],
  H:["display","drift","battery","cport","fan","water","ssd","software","mainboard"],
  P:["drift","cport","battery","buttons","water"],
  X:["hdmi","fan","drift","drive","psu","display","cport","battery","ssd","water","software","mainboard"]
};
const BASE = {
  phone:{display:[219,149],battery:99,port:99,back:119,camera:149,water:49,camglass:59,frontcam:119,faceid:199,speaker:99,earpiece:99,mic:99,mainboard:149,data:49,software:49,buttons:89,vibration:79,sim:89,jack:79,diagnosis:29},
  tablet:{display:[249,179],battery:129,port:119,back:149,camera:119,water:49,frontcam:109,speaker:99,mic:99,buttons:89,mainboard:179,data:49,software:49,diagnosis:29},
  laptop:{display:[449,329],battery:179,keyboard:199,port:149,fan:79,water:49,trackpad:179,hinge:149,ssd:129,speaker:129,mainboard:249,data:49,software:69,diagnosis:29},
  console:{hdmi:99,fan:69,drive:119,psu:129,ssd:89,water:49,software:49,mainboard:149,display:[159,109],drift:59,battery:79,cport:59,buttons:49,diagnosis:29}
};
const FIXED = new Set(["water","data","software","diagnosis"]);
const FROM = new Set(["mainboard","ssd"]);
const K = {display:1,back:.8,camera:.7,camglass:.3,frontcam:.5,faceid:.5,battery:.35,port:.4,speaker:.3,earpiece:.3,mic:.3,mainboard:.5,buttons:.3,vibration:.2,sim:.3,jack:.2,keyboard:.6,trackpad:.5,hinge:.5,fan:.2,ssd:.3,hdmi:.3,drive:.4,psu:.4,drift:.2,cport:.2};
/* Current TipTop shop prices (tiptophandyreparatur.de) used as anchors */
const REAL = {
  "phone-apple-iphone-13":{display:[219,149],back:119,battery:99,faceid:199,camglass:59,camera:149,frontcam:119,port:99,mic:99,speaker:99},
  "phone-apple-iphone-15":{display:[399,349],back:139,battery:99,faceid:249,camglass:59,camera:179,frontcam:129,port:119,mic:129,speaker:119}
};
const r9 = x => Math.max(19, Math.round(x / 10) * 10 - 1);

/* ===== Devices ===== */
const M = {
  phone:{
    Apple:"iPhone 17 Pro Max:2.5:Fp|iPhone 17 Pro:2.35:F|iPhone Air:2.2:F|iPhone 17:2.0:Fp|iPhone 16e:1.5:F|iPhone 16 Pro Max:2.35:F|iPhone 16 Pro:2.2:Fp|iPhone 16 Plus:2.0:F|iPhone 16:1.9:Fp|iPhone 15 Pro Max:2.1:F|iPhone 15 Pro:1.95:F|iPhone 15 Plus:1.85:F|iPhone 15:1.82:Fp|iPhone 14 Pro Max:1.6:F|iPhone 14 Pro:1.5:F|iPhone 14 Plus:1.2:F|iPhone 14:1.1:Fp|iPhone 13 Pro Max:1.35:F|iPhone 13 Pro:1.25:F|iPhone 13:1:Fp|iPhone 13 mini:0.95:F|iPhone 12 Pro Max:1.0:F|iPhone 12 Pro:0.95:F|iPhone 12:0.9:Fp|iPhone 12 mini:0.85:F|iPhone 11 Pro Max:0.9:F|iPhone 11 Pro:0.85:F|iPhone 11:0.75:Fp|iPhone XS Max:0.8:F|iPhone XS:0.75:F|iPhone XR:0.7:F|iPhone X:0.7:F|iPhone SE (2022):0.55:|iPhone SE (2020):0.5:|iPhone 8 Plus:0.55:|iPhone 8:0.5:",
    Samsung:"Galaxy S26 Ultra:2.4:p|Galaxy S26+:1.9:|Galaxy S26:1.7:|Galaxy S25 Ultra:2.3:p|Galaxy S25 Edge:1.9:|Galaxy S25+:1.8:|Galaxy S25:1.6:p|Galaxy S24 Ultra:2.1:|Galaxy S24+:1.6:|Galaxy S24:1.4:p|Galaxy S24 FE:1.0:|Galaxy S23 Ultra:1.9:|Galaxy S23:1.25:|Galaxy S23 FE:0.95:|Galaxy S22 Ultra:1.7:|Galaxy S22:1.1:|Galaxy S21 FE:0.85:|Galaxy Z Fold7:3.2:|Galaxy Z Flip7:2.2:|Galaxy Z Fold6:3.0:|Galaxy Z Flip6:2.0:|Galaxy A56:0.75:p|Galaxy A55:0.7:|Galaxy A54:0.65:|Galaxy A36:0.65:|Galaxy A35:0.6:|Galaxy A26:0.55:|Galaxy A25:0.5:|Galaxy A16:0.45:J|Galaxy A15:0.42:J",
    Google:"Pixel 10 Pro XL:2.0:|Pixel 10 Pro:1.8:|Pixel 10:1.4:|Pixel 9a:0.9:|Pixel 9 Pro XL:1.8:|Pixel 9 Pro:1.6:|Pixel 9:1.3:p|Pixel 8a:0.8:|Pixel 8 Pro:1.4:|Pixel 8:1.1:|Pixel 7a:0.7:|Pixel 7:0.9:",
    Xiaomi:"Xiaomi 15 Ultra:1.8:|Xiaomi 15:1.3:|Xiaomi 14T Pro:1.1:|Redmi Note 14 Pro:0.7:J|Redmi Note 13 Pro:0.6:J|Redmi Note 13:0.5:J|Poco F7 Pro:0.9:|Poco X7 Pro:0.7:",
    Huawei:"P60 Pro:1.5:|P40 Pro:1.2:|P30 Pro:1.0:|P30:0.8:J|Mate 20 Pro:0.9:|P smart 2021:0.4:J",
    OnePlus:"OnePlus 13:1.5:|OnePlus 12:1.3:|OnePlus Nord 4:0.8:|OnePlus Nord CE4:0.6:J",
    Oppo:"Find X8 Pro:1.6:|Reno12 Pro:0.9:|Oppo A80:0.5:J",
    Sony:"Xperia 1 VI:1.6:J|Xperia 10 VI:0.7:J",
    Motorola:"Edge 50 Pro:0.9:|Moto g85:0.5:J"
  },
  tablet:{
    Apple:"iPad Pro 13 (M5):2.5:|iPad Pro 11 (M5):2.1:|iPad Pro 13 (M4):2.4:|iPad Pro 11 (M4):2.0:p|iPad Pro 12.9 (6th gen):1.9:|iPad Pro 11 (4th gen):1.6:|iPad Air 13 (M3):1.6:|iPad Air 11 (M3):1.3:p|iPad Air 11 (M2):1.3:|iPad Air (5th gen):1.1:|iPad (A16):1.0:p|iPad (10th gen):1.0:p|iPad (9th gen):0.7:p|iPad mini (A17 Pro):1.2:|iPad mini (6th gen):1.1:",
    Samsung:"Galaxy Tab S10 Ultra:2.0:|Galaxy Tab S10+:1.7:|Galaxy Tab S9 FE:1.0:p|Galaxy Tab A9+:0.6:p",
    Lenovo:"Lenovo Tab P12:0.8:|Lenovo Tab M11:0.6:",
    Xiaomi:"Xiaomi Pad 7:0.8:|Redmi Pad Pro:0.6:",
    Huawei:"MatePad 11.5:0.8:"
  },
  laptop:{
    Apple:"MacBook Pro 16 (M4):1.9:|MacBook Pro 14 (M5):1.75:|MacBook Pro 14 (M4):1.7:p|MacBook Pro 14 (M3):1.6:|MacBook Pro 13 (M2):1.2:|MacBook Pro 13 (M1):1.1:p|MacBook Air 15 (M4):1.4:|MacBook Air 13 (M4):1.25:p|MacBook Air 13 (M3):1.2:|MacBook Air (M2):1.15:p|MacBook Air (M1):1.0:p|MacBook (Intel):0.9:",
    Lenovo:"ThinkPad:0.8:p|IdeaPad:0.6:|Yoga:0.8:|Legion:0.9:",
    HP:"EliteBook:0.8:|Pavilion:0.6:p|Envy:0.7:|Omen:0.9:",
    Dell:"XPS:1.0:p|Latitude:0.8:|Inspiron:0.6:",
    ASUS:"ZenBook:0.8:|VivoBook:0.6:|ROG:1.0:",
    Acer:"Aspire:0.55:|Swift:0.7:|Nitro:0.8:",
    Microsoft:"Surface Laptop:1.0:|Surface Pro:1.1:",
    MSI:"MSI Gaming:0.9:",
    Samsung:"Galaxy Book:0.8:",
    Huawei:"MateBook:0.8:"
  },
  console:{
    Sony:"PlayStation 5 Pro:1.3:bp|PlayStation 5:1.0:Bp|PlayStation 5 Digital:1.0:b|PlayStation 4 Pro:0.85:B|PlayStation 4:0.75:B|DualSense controller:0.8:Pp|DualShock 4 controller:0.7:P",
    Microsoft:"Xbox Series X:1.1:Bp|Xbox Series S:0.9:b|Xbox One X:0.85:B|Xbox One S:0.8:B|Xbox controller:0.7:P",
    Nintendo:"Switch 2:1.4:Hp|Switch OLED:1.1:Hp|Switch:1.0:H|Switch Lite:0.9:H|Joy-Con:0.6:P",
    Valve:"Steam Deck OLED:1.3:H|Steam Deck:1.1:H"
  }
};
const CATS = ["phone","tablet","laptop","console"];
let ADDED = LS.get("tt-added", []);
let OVR = LS.get("tt-ovr", {});
let REQS = LS.get("tt-reqs", []);
let MODELS = {}, ALIASES = [];
const mk = (cat, brand, name, f, fl, added) => ({ id:slug(cat + "-" + brand + "-" + name), cat, brand, name, f, fl:fl || "", added:!!added });

function buildModels() {
  MODELS = {};
  for (const c of CATS) {
    MODELS[c] = [];
    for (const b in M[c]) for (const e of M[c][b].split("|")) { const [n, f, fl] = e.split(":"); MODELS[c].push(mk(c, b, n, +f, fl)); }
  }
  for (const a of ADDED) if (MODELS[a.cat]) MODELS[a.cat].unshift(mk(a.cat, a.brand, a.name, a.f, a.fl, true));
  ALIASES = [];
  const add = (a, m) => { a = norm(a).trim(); if (a.length >= 3) ALIASES.push({ a, m }); };
  for (const c of CATS) for (const m of MODELS[c]) {
    const n = norm(m.name).trim();
    add(m.name, m); add(m.brand + " " + m.name, m);
    add(n.replace(/([a-z])\s(\d)/g, "$1$2"), m);
    if (m.brand === "Samsung") add(n.replace(/^galaxy /, ""), m);
    if (/^playstation /.test(n)) add(n.replace(/^playstation /, "ps"), m);
    if (/^xbox (series|one)/.test(n)) add(n.replace(/^xbox /, ""), m);
  }
}
const brandsOf = c => [...new Set(MODELS[c].map(m => m.brand))];
function locName(s) { return lang === "de" ? s.replace(/\((\d+)(st|nd|rd|th) gen\)/, "($1. Gen.)").replace(/ controller$/, " Controller") : s; }
function fullName(m) {
  if (m.custom) return m.name;
  const n = m.name.toLowerCase().startsWith(m.brand.toLowerCase()) ? m.name : m.brand + " " + m.name;
  return locName(n);
}
function servicesFor(m) {
  if (!m) return [];
  if (m.cat === "phone") return LISTS.phone.filter(k => (k !== "faceid" || m.fl.includes("F") || m.custom) && (k !== "jack" || m.fl.includes("J") || m.custom));
  if (m.cat === "console") { const kind = (m.fl.match(/[BbHPX]/) || [m.custom ? "X" : "B"])[0]; return CON[kind]; }
  return LISTS[m.cat];
}
function price(m, key, tier, noOvr) {
  const ok = m.id + "|" + key + (tier ? "|" + tier : "");
  if (!noOvr && OVR[ok] != null) return OVR[ok];
  const base = BASE[m.cat][key];
  if (base == null) return null;
  if (FIXED.has(key)) return base;
  if (m.custom) return null;
  const real = (REAL[m.id] || {})[key];
  if (real != null) return Array.isArray(real) ? real[tier === "o" ? 0 : 1] : real;
  const b = Array.isArray(base) ? base[tier === "o" ? 0 : 1] : base;
  return r9(b * Math.pow(m.f, K[key] == null ? .5 : K[key]));
}
function priceLabel(m, key) {
  if (key === "display") {
    const p = price(m, "display", "p"), o = price(m, "display", "o");
    if (p == null && o == null) return t("on_request");
    return t("from") + " " + fmt(Math.min(p == null ? Infinity : p, o == null ? Infinity : o));
  }
  const v = price(m, key);
  if (v == null) return t("on_request");
  return (FROM.has(key) ? t("from") + " " : "") + fmt(v);
}
function totalOf(m, sel) {
  let sum = 0, unknown = 0, from = false;
  for (const s of sel) { const v = price(m, s.key, s.tier); if (v == null) unknown++; else sum += v; if (FROM.has(s.key)) from = true; }
  if (unknown && unknown === sel.length) return { text:t("on_request"), sum:null };
  let text = (from ? t("from") + " " : "") + fmt(sum);
  return { text, sum, extra:unknown ? t("plus_req") : "" };
}

