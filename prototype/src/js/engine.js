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
  drift:["Joystick drift","Joystick-Drift Reparatur"], tmr:["TMR joysticks (no more drift)","TMR-Joysticks (driftfrei)"], cport:["Charging port","Ladebuchse Reparatur"]
};
const SV_CAT = {
  tablet:{ back:["Housing and back","Gehäuse und Rückseite"] },
  laptop:{ back:["Housing","Gehäuse Reparatur"], port:["Charging port / DC jack","Ladebuchse / DC-Buchse"], software:["Operating system and software","Betriebssystem und Software"] },
  console:{ display:["Screen (handheld)","Bildschirm (Handheld)"], fan:["Overheating and cleaning","Überhitzung und Reinigung"], software:["Software and firmware","Software und Firmware"], ssd:["Storage upgrade","Speicher-Upgrade"], battery:["Battery","Akku Austausch"] }
};
const svName = (k, cat) => { const o = (SV_CAT[cat] || {})[k] || SV[k] || [k, k]; return o[lang === "de" ? 1 : 0]; };
const ICON_OF = { cport:"port", tmr:"drift" };

const LISTS = {
  phone:["display","battery","port","back","camera","water","camglass","frontcam","faceid","speaker","earpiece","mic","mainboard","data","software","buttons","vibration","sim","jack"],
  tablet:["display","battery","port","back","camera","water","frontcam","speaker","mic","buttons","mainboard","data","software"],
  laptop:["display","battery","keyboard","port","fan","water","trackpad","hinge","ssd","speaker","mainboard","data","software"]
};
const CON = {
  // Owner, 25 Nov 2026: joystick drift and TMR sticks belong on the console page too (the controller comes with it).
  B:["hdmi","drift","tmr","fan","drive","psu","ssd","water","software","mainboard"],
  b:["hdmi","drift","tmr","fan","psu","ssd","water","software","mainboard"],
  H:["display","drift","tmr","battery","cport","fan","water","ssd","software","mainboard"],
  P:["drift","tmr","cport","battery","buttons","water"],
  X:["hdmi","fan","drift","drive","psu","display","cport","battery","ssd","water","software","mainboard"]
};
const BASE = {
  phone:{display:[219,149],battery:99,port:99,back:119,camera:149,water:49,camglass:59,frontcam:119,faceid:199,speaker:99,earpiece:99,mic:99,mainboard:149,data:49,software:49,buttons:89,vibration:79,sim:89,jack:79,diagnosis:29},
  tablet:{display:[249,179],battery:129,port:119,back:149,camera:119,water:49,frontcam:109,speaker:99,mic:99,buttons:89,mainboard:179,data:49,software:49,diagnosis:29},
  laptop:{display:[449,329],battery:179,keyboard:199,port:149,fan:79,water:49,trackpad:179,hinge:149,ssd:129,speaker:129,mainboard:249,data:49,software:69,diagnosis:29},
  console:{hdmi:99,fan:69,drive:119,psu:129,ssd:89,water:49,software:49,mainboard:149,display:[159,109],drift:59,tmr:79,battery:79,cport:59,buttons:49,diagnosis:29}
};
const FIXED = new Set(["water","data","software","diagnosis"]);
const FROM = new Set(["mainboard","ssd"]);
const K = {display:1,back:.8,camera:.7,camglass:.3,frontcam:.5,faceid:.5,battery:.35,port:.4,speaker:.3,earpiece:.3,mic:.3,mainboard:.5,buttons:.3,vibration:.2,sim:.3,jack:.2,keyboard:.6,trackpad:.5,hinge:.5,fan:.2,ssd:.3,hdmi:.3,drive:.4,psu:.4,drift:.2,tmr:.2,cport:.2};
/* Current TipTop shop prices (tiptophandyreparatur.de) used as anchors */
const REAL = {
  "phone-apple-iphone-13":{display:[219,149],back:119,battery:99,faceid:199,camglass:59,camera:149,frontcam:119,port:99,mic:99,speaker:99},
  "phone-apple-iphone-15":{display:[399,349],back:139,battery:99,faceid:249,camglass:59,camera:179,frontcam:129,port:119,mic:129,speaker:119}
};
const r9 = x => Math.max(19, Math.round(x / 10) * 10 - 1);

/* ===== Devices ===== */
const M = {
  phone:{
    Apple:"iPhone 18 Pro Max:2.7:Fp|iPhone 18 Pro:2.55:Fp|iPhone Duo:3.6:p|iPhone 17 Pro Max:2.5:Fp|iPhone 17 Pro:2.35:F|iPhone Air:2.2:F|iPhone 17:2.0:Fp|iPhone 17e:1.6:F|iPhone 16e:1.5:F|iPhone 16 Pro Max:2.35:F|iPhone 16 Pro:2.2:Fp|iPhone 16 Plus:2.0:F|iPhone 16:1.9:Fp|iPhone 15 Pro Max:2.1:F|iPhone 15 Pro:1.95:F|iPhone 15 Plus:1.85:F|iPhone 15:1.82:Fp|iPhone 14 Pro Max:1.6:F|iPhone 14 Pro:1.5:F|iPhone 14 Plus:1.2:F|iPhone 14:1.1:Fp|iPhone 13 Pro Max:1.35:F|iPhone 13 Pro:1.25:F|iPhone 13:1:Fp|iPhone 13 mini:0.95:F|iPhone 12 Pro Max:1.0:F|iPhone 12 Pro:0.95:F|iPhone 12:0.9:Fp|iPhone 12 mini:0.85:F|iPhone 11 Pro Max:0.9:F|iPhone 11 Pro:0.85:F|iPhone 11:0.75:Fp|iPhone XS Max:0.8:F|iPhone XS:0.75:F|iPhone XR:0.7:F|iPhone X:0.7:F|iPhone SE (2022):0.55:|iPhone SE (2020):0.5:|iPhone 8 Plus:0.55:|iPhone 8:0.5:",
    Samsung:"Galaxy S26 Ultra:2.4:p|Galaxy S26+:1.9:|Galaxy S26:1.7:|Galaxy S25 Ultra:2.3:p|Galaxy S25 Edge:1.9:|Galaxy S25+:1.8:|Galaxy S25:1.6:p|Galaxy S25 FE:1.2:|Galaxy S24 Ultra:2.1:|Galaxy S24+:1.6:|Galaxy S24:1.4:p|Galaxy S24 FE:1.0:|Galaxy S23 Ultra:1.9:|Galaxy S23+:1.5:|Galaxy S23:1.25:|Galaxy S23 FE:0.95:|Galaxy S22 Ultra:1.7:|Galaxy S22+:1.3:|Galaxy S22:1.1:|Galaxy S21 Ultra:1.5:|Galaxy S21+:1.15:|Galaxy S21:1.0:|Galaxy S21 FE:0.85:|Galaxy S20 Ultra:1.3:|Galaxy S20+:1.0:|Galaxy S20:0.95:|Galaxy S20 FE:0.8:|Galaxy S10+:0.9:J|Galaxy S10:0.85:J|Galaxy S10e:0.75:J|Galaxy Z Fold7:3.2:|Galaxy Z Flip7:2.2:|Galaxy Z Flip7 FE:1.8:|Galaxy Z Fold6:3.0:|Galaxy Z Flip6:2.0:|Galaxy Z Fold5:2.8:|Galaxy Z Flip5:2.0:|Galaxy Z Fold4:2.6:|Galaxy Z Flip4:1.8:|Galaxy Z Fold3:2.4:|Galaxy Z Flip3:1.6:|Galaxy Note20 Ultra:1.5:|Galaxy Note20:1.1:|Galaxy Note10+:1.1:|Galaxy Note10:0.95:|Galaxy A56:0.75:p|Galaxy A55:0.7:|Galaxy A54:0.65:|Galaxy A53:0.6:|Galaxy A52s:0.6:J|Galaxy A52:0.55:J|Galaxy A51:0.5:J|Galaxy A36:0.65:|Galaxy A35:0.6:|Galaxy A34:0.55:|Galaxy A33:0.5:|Galaxy A32:0.45:J|Galaxy A26:0.55:|Galaxy A25:0.5:|Galaxy A17:0.45:J|Galaxy A16:0.45:J|Galaxy A15:0.42:J|Galaxy A14:0.4:J|Galaxy A13:0.4:J|Galaxy A12:0.35:J|Galaxy A06:0.35:J|Galaxy A05s:0.35:J",
    Google:"Pixel 10 Pro Fold:2.6:|Pixel 10 Pro XL:2.0:|Pixel 10 Pro:1.8:|Pixel 10:1.4:|Pixel 9a:0.9:|Pixel 9 Pro Fold:2.5:|Pixel 9 Pro XL:1.8:|Pixel 9 Pro:1.6:|Pixel 9:1.3:p|Pixel 8a:0.8:|Pixel 8 Pro:1.4:|Pixel 8:1.1:|Pixel 7a:0.7:|Pixel 7 Pro:1.2:|Pixel 7:0.9:|Pixel Fold:2.3:|Pixel 6a:0.7:|Pixel 6 Pro:1.1:|Pixel 6:0.9:|Pixel 5:0.75:|Pixel 4a:0.6:J",
    Xiaomi:"Xiaomi 15 Ultra:1.8:|Xiaomi 15:1.3:|Xiaomi 15T Pro:1.2:|Xiaomi 15T:1.0:|Xiaomi 14 Ultra:1.7:|Xiaomi 14:1.2:|Xiaomi 14T Pro:1.1:|Xiaomi 14T:0.95:|Xiaomi 13:1.1:|Xiaomi 13T Pro:1.0:|Xiaomi 13T:0.9:|Xiaomi 12:0.95:|Xiaomi 12T Pro:0.95:|Xiaomi 11T Pro:0.85:|Redmi Note 14 Pro+:0.8:|Redmi Note 14 Pro:0.7:J|Redmi Note 14:0.5:J|Redmi Note 13 Pro+:0.7:|Redmi Note 13 Pro:0.6:J|Redmi Note 13:0.5:J|Redmi Note 12 Pro:0.55:J|Redmi Note 12:0.45:J|Redmi Note 11:0.4:J|Redmi 14C:0.35:J|Redmi 13C:0.35:J|Redmi 12:0.35:J|Redmi A3:0.3:J|Poco F7 Pro:0.9:|Poco F7:0.85:|Poco F6:0.8:|Poco X7 Pro:0.7:|Poco X7:0.6:|Poco X6 Pro:0.6:|Poco M6 Pro:0.45:J",
    Huawei:"Pura 70 Ultra:1.8:|Pura 70 Pro:1.6:|P60 Pro:1.5:|P50 Pro:1.4:|P40 Pro:1.2:|P40:0.9:|P30 Pro:1.0:|P30:0.8:J|P30 lite:0.5:J|P20 Pro:0.8:|P20:0.6:|Mate 40 Pro:1.3:|Mate 30 Pro:1.1:|Mate 20 Pro:0.9:|Nova 11:0.6:|Nova 9:0.55:|P smart 2021:0.4:J|P smart 2019:0.35:J",
    OnePlus:"OnePlus 15:1.6:|OnePlus 13:1.5:|OnePlus 13R:1.1:|OnePlus 12:1.3:|OnePlus 12R:1.0:|OnePlus 11:1.1:|OnePlus 10 Pro:1.1:|OnePlus 9 Pro:1.0:|OnePlus 9:0.85:|OnePlus 8T:0.8:|OnePlus 8 Pro:0.9:|OnePlus Nord 5:0.8:|OnePlus Nord 4:0.8:|OnePlus Nord CE4:0.6:J|OnePlus Nord CE4 Lite:0.5:J|OnePlus Nord 3:0.7:|OnePlus Nord CE3 Lite:0.45:J",
    Oppo:"Find X9 Pro:1.7:|Find X8 Pro:1.6:|Find X8:1.4:|Find X5 Pro:1.3:|Find X3 Pro:1.1:|Reno13 Pro:1.0:|Reno13:0.85:|Reno12 Pro:0.9:|Reno11 F:0.6:|Reno10 Pro:0.8:|Oppo A80:0.5:J|Oppo A79:0.45:J|Oppo A78:0.45:J|Oppo A60:0.4:J|Oppo A58:0.4:J|Oppo A38:0.35:J|Oppo A18:0.35:J",
    Sony:"Xperia 1 VII:1.7:J|Xperia 10 VII:0.75:J|Xperia 1 VI:1.6:J|Xperia 10 VI:0.7:J|Xperia 1 V:1.5:J|Xperia 5 V:1.3:J|Xperia 10 V:0.65:J|Xperia 1 IV:1.4:J|Xperia 5 IV:1.2:J|Xperia 10 IV:0.6:J",
    Motorola:"Edge 60 Pro:0.95:|Edge 60:0.8:|Edge 60 Fusion:0.7:|Edge 50 Ultra:1.0:|Edge 50 Pro:0.9:|Edge 50 Fusion:0.7:|Edge 40 Neo:0.65:|razr 60 ultra:1.9:|razr 60:1.4:|razr 50 ultra:1.8:|razr 50:1.3:|razr 40 ultra:1.6:|Moto g86:0.5:J|Moto g85:0.5:J|Moto g75:0.5:J|Moto g55:0.45:J|Moto g54:0.45:J|Moto g35:0.4:J|Moto g24:0.35:J|Moto g15:0.3:J|Moto e14:0.3:J",
    Honor:"Magic V5:2.8:|Magic7 Pro:1.6:|Magic6 Pro:1.5:|Honor 400 Pro:1.1:|Honor 400:0.9:|Honor 200 Pro:1.0:|Honor 200:0.8:|Magic7 Lite:0.6:|Honor X8c:0.45:",
    Nothing:"Phone (3):1.2:|Phone (3a) Pro:0.8:|Phone (3a):0.7:|Phone (2a):0.6:|Phone (2):0.9:|Phone (1):0.75:|CMF Phone 2 Pro:0.45:",
    Fairphone:"Fairphone 6:0.7:|Fairphone 5:0.65:|Fairphone 4:0.55:",
    Realme:"GT 7 Pro:1.1:|GT 6:0.8:|realme 14 Pro+:0.7:|realme 12 Pro+:0.65:|realme C67:0.35:J"
  },
  tablet:{
    Apple:"iPad Pro 13 (M5):2.5:|iPad Pro 11 (M5):2.1:|iPad Pro 13 (M4):2.4:|iPad Pro 11 (M4):2.0:p|iPad Pro 12.9 (6th gen):1.9:|iPad Pro 11 (4th gen):1.6:|iPad Pro 12.9 (5th gen):1.8:|iPad Pro 11 (3rd gen):1.5:|iPad Air 13 (M3):1.6:|iPad Air 11 (M3):1.3:p|iPad Air 11 (M2):1.3:|iPad Air (5th gen):1.1:|iPad Air (4th gen):1.1:|iPad (A16):1.0:p|iPad (10th gen):1.0:p|iPad (9th gen):0.7:p|iPad (8th gen):0.75:|iPad (7th gen):0.7:|iPad mini (A17 Pro):1.2:|iPad mini (6th gen):1.1:|iPad mini (5th gen):0.8:",
    Samsung:"Galaxy Tab S10 Ultra:2.0:|Galaxy Tab S10+:1.7:|Galaxy Tab S10 FE+:1.2:|Galaxy Tab S10 FE:1.05:|Galaxy Tab S9 Ultra:1.9:|Galaxy Tab S9+:1.6:|Galaxy Tab S9:1.4:|Galaxy Tab S9 FE:1.0:p|Galaxy Tab S8 Ultra:1.8:|Galaxy Tab S8:1.3:|Galaxy Tab S7 FE:0.9:|Galaxy Tab S6 Lite:0.6:|Galaxy Tab A9+:0.6:p|Galaxy Tab A9:0.5:|Galaxy Tab A8:0.5:",
    Lenovo:"Lenovo Tab P12:0.8:|Lenovo Tab M11:0.6:|Lenovo Tab Plus:0.7:|Lenovo Tab P11 (2nd gen):0.7:|Lenovo Tab M10 Plus:0.5:",
    Xiaomi:"Xiaomi Pad 7:0.8:|Redmi Pad Pro:0.6:|Redmi Pad 2:0.5:|Xiaomi Pad 6:0.7:|Redmi Pad SE:0.45:",
    Huawei:"MatePad Pro 13.2:1.4:|MatePad 11.5:0.8:|MatePad 11:0.75:|MatePad SE:0.45:"
  },
  laptop:{
    Apple:"MacBook Pro 16 (M4):1.9:|MacBook Pro 14 (M5):1.75:|MacBook Pro 14 (M4):1.7:p|MacBook Pro 16 (M3):1.85:|MacBook Pro 14 (M3):1.6:|MacBook Pro 16 (M2 Pro):1.7:|MacBook Pro 14 (M2 Pro):1.5:|MacBook Pro 16 (M1 Pro):1.6:|MacBook Pro 14 (M1 Pro):1.4:|MacBook Pro 13 (M2):1.2:|MacBook Pro 13 (M1):1.1:p|MacBook Air 15 (M4):1.4:|MacBook Air 13 (M4):1.25:p|MacBook Air 15 (M3):1.25:|MacBook Air 13 (M3):1.2:|MacBook Air 15 (M2):1.2:|MacBook Air (M2):1.15:p|MacBook Air (M1):1.0:p|MacBook Pro 16 (Intel):1.3:|MacBook Pro 13 (Intel):1.0:|MacBook Air (Intel):0.85:|MacBook (Intel):0.9:",
    Lenovo:"ThinkPad:0.8:p|ThinkBook:0.7:|IdeaPad:0.6:|IdeaPad Gaming:0.75:|Yoga:0.8:|Yoga Slim:0.8:|Legion:0.9:|LOQ:0.75:",
    HP:"EliteBook:0.8:|ProBook:0.7:|ZBook:1.0:|Spectre:1.0:|Envy:0.7:|OmniBook:0.8:|Pavilion:0.6:p|HP Laptop 15:0.5:|Omen:0.9:|Victus:0.75:",
    Dell:"XPS:1.0:p|Latitude:0.8:|Precision:1.0:|Inspiron:0.6:|Vostro:0.6:|Alienware:1.2:|Dell G15:0.8:",
    ASUS:"ZenBook:0.8:|VivoBook:0.6:|Vivobook Pro:0.75:|ExpertBook:0.7:|ROG Zephyrus:1.1:|ROG Strix:1.0:|ROG:1.0:|TUF Gaming:0.8:",
    Acer:"Swift:0.7:|Swift Go:0.75:|Aspire:0.55:|TravelMate:0.6:|Chromebook:0.45:|Nitro:0.8:|Predator:1.0:",
    Microsoft:"Surface Laptop:1.0:|Surface Laptop Studio:1.3:|Surface Laptop Go:0.7:|Surface Pro:1.1:|Surface Go:0.6:|Surface Book:1.1:",
    MSI:"Stealth:1.1:|Raider:1.2:|Katana:0.8:|MSI Gaming:0.9:|Prestige:0.8:|Modern:0.6:",
    Samsung:"Galaxy Book5 Pro:1.0:|Galaxy Book4 Pro:0.95:|Galaxy Book4:0.75:|Galaxy Book:0.8:",
    Huawei:"MateBook X Pro:1.1:|MateBook:0.8:|MateBook D 16:0.6:|MateBook D 14:0.55:"
  },
  console:{
    Sony:"PlayStation 5 Pro:1.3:bp|PlayStation 5:1.0:Bp|PlayStation 5 Digital:1.0:b|PlayStation 4 Pro:0.85:B|PlayStation 4 Slim:0.75:B|PlayStation 4:0.75:B|PlayStation 3:0.7:B|PlayStation Portal:0.8:H|DualSense Edge controller:1.0:P|DualSense controller:0.8:Pp|DualShock 4 controller:0.7:P",
    Microsoft:"Xbox Series X:1.1:Bp|Xbox Series S:0.9:b|Xbox One X:0.85:B|Xbox One S:0.8:B|Xbox One:0.75:B|Xbox 360:0.65:B|Xbox Elite controller:1.0:P|Xbox controller:0.7:P",
    Nintendo:"Switch 2:1.4:Hp|Switch OLED:1.1:Hp|Switch:1.0:H|Switch Lite:0.9:H|Joy-Con 2:0.7:P|Joy-Con:0.6:P|Switch Pro Controller:0.7:P",
    Valve:"Steam Deck OLED:1.3:H|Steam Deck:1.1:H",
    ASUS:"ROG Xbox Ally X:1.5:H|ROG Ally X:1.3:H|ROG Ally:1.2:H",
    Lenovo:"Legion Go:1.3:H|Legion Go S:1.1:H",
    MSI:"MSI Claw:1.2:H"
  }
};
const CATS = ["phone","tablet","laptop","console"];
let ADDED = LS.get("tt-added", []);
let OVR = LS.get("tt-ovr", {});
let REQS = LS.get("tt-reqs", []);
let MODELS = {}, ALIASES = [];
const ALIAS_STOP = new Set(["one","book","modern","stealth","raider","swift","precision","prestige"]);
const mk = (cat, brand, name, f, fl, added) => ({ id:slug(cat + "-" + brand + "-" + name.replace(/\+/g, " plus")), cat, brand, name, f, fl:fl || "", added:!!added });

function buildModels() {
  MODELS = {};
  for (const c of CATS) {
    MODELS[c] = [];
    for (const b in M[c]) for (const e of M[c][b].split("|")) { const [n, f, fl] = e.split(":"); MODELS[c].push(mk(c, b, n, +f, fl)); }
  }
  for (const a of ADDED) if (MODELS[a.cat]) MODELS[a.cat].unshift(mk(a.cat, a.brand, a.name, a.f, a.fl, true));
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
const brandsOf = c => [...new Set(MODELS[c].map(m => m.brand))];
function locName(s) { return lang === "de" ? s.replace(/\((\d+)(st|nd|rd|th) gen\)/, "($1. Gen.)").replace(/ controller$/, " Controller") : s; }
function fullName(m) {
  if (m.custom) return m.name;
  const n = m.name.toLowerCase().startsWith(m.brand.toLowerCase()) ? m.name : m.brand + " " + m.name;
  return locName(n);
}
// Repairs a model physically can't have (no fan, soldered storage, no charging port, AA batteries).
const NOSV = { "Sony|PlayStation Portal":["fan","ssd"], "Nintendo|Switch 2":["ssd"], "Nintendo|Switch OLED":["ssd"], "Nintendo|Switch":["ssd"], "Nintendo|Switch Lite":["ssd"],
  "Nintendo|Joy-Con":["cport"], "Nintendo|Joy-Con 2":["cport"], "Microsoft|Xbox controller":["battery"] };
// Apple silicon MacBooks: SSD soldered to the board; MacBook Air (M1 onward) has no fan.
const noSv = m => NOSV[m.brand + "|" + m.name] || (m.cat === "laptop" && m.brand === "Apple" && /\(M\d/.test(m.name) ? (/^MacBook Air/.test(m.name) ? ["ssd","fan"] : ["ssd"]) : []);
function servicesFor(m) {
  if (!m) return [];
  const x = noSv(m);
  if (x.length) return servicesForAll(m).filter(k => !x.includes(k));
  return servicesForAll(m);
}
function servicesForAll(m) {
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

