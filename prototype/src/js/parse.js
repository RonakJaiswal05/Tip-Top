/* ===== Smart assistant (text + voice) ===== */
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
