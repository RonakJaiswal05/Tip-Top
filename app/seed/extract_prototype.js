// Extracts the data the Django seed needs from prototype/index.html (texts, catalogue, legal pages).
// Run from the repo root: node app/seed/extract_prototype.js  -> app/seed/prototype.json
// The catalogue part of index.html is prototype/src/js/engine.js, spliced in by prototype/src/assemble.py.
const fs = require("fs"), vm = require("vm"), path = require("path");
const root = path.resolve(__dirname, "..", "..");
const lines = fs.readFileSync(path.join(root, "prototype", "index.html"), "utf8").split(/\r?\n/);
const find = (re, from = 0) => { for (let i = from; i < lines.length; i++) if (re.test(lines[i])) return i; throw new Error("not found: " + re); };
const seg = (a, b) => lines.slice(a, b).join("\n");
const s0 = find(/^const WA_NUMBER/), s1 = find(/^\$\("bld"\)\.addEventListener\("click"/);
const sh0 = find(/^const SHOPS = \[/), sh1 = find(/^const mapsUrl/);
const bw0 = find(/^const BRANDWALL = \[/), bw1 = find(/^function renderBrands/);

const lg0 = find(/^const LEGAL_KEYS/), lg1 = find(/^\/\* ===== Legal pages, cookie consent/);
const gm0 = find(/^const GMB = \{/), gm1 = find(/^const gmbUrl/);
// Every later "Object.assign(T.en, {...})" / "Object.assign(T.de, {...})" block adds texts (ratings, buyback photos,
// multi-select, search, ...). Collect each one up to its closing "});".
const blocks = [];
for (let i = 0; i < lines.length; i++) {
  if (i >= s0 && i < s1) continue;
  if (/^Object\.assign\(T\.(en|de), \{/.test(lines[i])) {
    let j = i; while (!/\}\);\s*$/.test(lines[j])) j++;
    blocks.push(seg(i, j + 1)); i = j;
  }
}
const code = [seg(s0, s1), seg(sh0, sh1), seg(bw0, bw1), seg(lg0, lg1), ...blocks, seg(gm0, gm1)].join("\n") + `
;buildModels();
const PRICES = [];
for (const c of CATS) for (const m of MODELS[c]) {
  const row = {};
  for (const k of [...servicesFor(m), "diagnosis"]) row[k] = k === "display" ? [price(m, k, "p"), price(m, k, "o")] : price(m, k);
  PRICES.push({ id:m.id, cat:m.cat, brand:m.brand, name:m.name, f:m.f, fl:m.fl, services:servicesFor(m), all:servicesForAll(m), prices:row,
    full_de:(lang = "de", fullName(m)), full_en:(lang = "en", fullName(m)) });
}
lang = "en";
;OUT = { PRICES, T, SV, SV_CAT, LISTS, CON, BASE, FIXED:[...FIXED], FROM:[...FROM], K, REAL, M, CATS, TOP6, KW, CATW, BRANDW, IMGS, REP_IMG, CAT_IMG,
  REP_CAT, REP_AND, IMG_HAVE:[...IMG_HAVE], ICON_OF, ALIAS_STOP:[...ALIAS_STOP], SHOPS, BRANDWALL, BRAND_LOGO, BRAND_LOGOS_READY:[...BRAND_LOGOS_READY],
  BRAND_WORDMARK, LEGAL_KEYS, LEGAL_UPD, LEGAL_DE, LEGAL_EN, LG_OWNER, LG_FIRM, COOKIES, GMB, IC, WA_NUMBER };`;
const ctx = { matchMedia: () => ({ matches:false, addEventListener(){} }), document: { documentElement: { classList: { add(){} } } },
  localStorage: { getItem(){ return null; }, setItem(){} }, console, OUT:null, Intl, Math, JSON, Set, Object, String, Array, Number, RegExp,
  encodeURIComponent, window:{} };
vm.createContext(ctx);
vm.runInContext(code, ctx);
const out = path.join(__dirname, "prototype.json");
fs.writeFileSync(out, JSON.stringify(ctx.OUT, null, 1));
const o = ctx.OUT; let n = 0; for (const c of o.CATS) for (const b in o.M[c]) n += o.M[c][b].split("|").length;
const brands = new Set(); for (const c of o.CATS) for (const b in o.M[c]) brands.add(b);
let prices = 0; for (const p of o.PRICES) for (const v of Object.values(p.prices)) prices += Array.isArray(v) ? 2 : 1;
console.log("wrote", out, "models:", n, "brands:", brands.size, "services:", Object.keys(o.SV).length, "prices:", prices,
  "T.de keys:", Object.keys(o.T.de).length, "T.en keys:", Object.keys(o.T.en).length);
