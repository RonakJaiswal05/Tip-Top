// Extracts the data the Django seed needs from prototype/index.html (texts, catalogue, legal pages).
// Run from the repo root: node app/seed/extract_prototype.js  -> app/seed/prototype.json
const fs = require("fs"), vm = require("vm"), path = require("path");
const root = path.resolve(__dirname, "..", "..");
const lines = fs.readFileSync(path.join(root, "prototype", "index.html"), "utf8").split(/\r?\n/);
const find = (re, from = 0) => { for (let i = from; i < lines.length; i++) if (re.test(lines[i])) return i; throw new Error("not found: " + re); };
const seg = (a, b) => lines.slice(a, b).join("\n");
const s0 = find(/^const WA_NUMBER/), s1 = find(/^\$\("bld"\)\.addEventListener\("click"/);
const sh0 = find(/^const SHOPS = \[/), sh1 = find(/^const mapsUrl/);
const bw0 = find(/^const BRANDWALL = \[/), bw1 = find(/^function renderBrands/);
const lg0 = find(/^const LEGAL_KEYS/), lg1 = find(/^\/\* ===== Legal pages, cookie consent/);
const ta0 = lg1 + 1, ta1 = find(/^function fine\(k\)/);
const gm0 = find(/^const GMB = \{/), gm1 = find(/^const gmbUrl/);
const code = [seg(s0, s1), seg(sh0, sh1), seg(bw0, bw1), seg(lg0, lg1), seg(ta0, ta1), seg(gm0, gm1)].join("\n") + `
;OUT = { T, SV, SV_CAT, LISTS, CON, BASE, FIXED:[...FIXED], FROM:[...FROM], K, REAL, M, CATS, TOP6, KW, CATW, BRANDW, IMGS, REP_IMG, CAT_IMG,
  SHOPS, BRANDWALL, BRAND_LOGO, LEGAL_KEYS, LEGAL_UPD, LEGAL_DE, LEGAL_EN, COOKIES, GMB, IC, WA_NUMBER };`;
const ctx = { matchMedia: () => ({ matches:false, addEventListener(){} }), document: { documentElement: { classList: { add(){} } } },
  localStorage: { getItem(){ return null; }, setItem(){} }, console, OUT:null, Intl, Math, JSON, Set, Object, String, Array, Number, RegExp, encodeURIComponent };
vm.createContext(ctx);
vm.runInContext(code, ctx);
const out = path.join(__dirname, "prototype.json");
fs.writeFileSync(out, JSON.stringify(ctx.OUT, null, 1));
const o = ctx.OUT; let n = 0; for (const c of o.CATS) for (const b in o.M[c]) n += o.M[c][b].split("|").length;
console.log("wrote", out, "models:", n, "services:", Object.keys(o.SV).length, "T.de keys:", Object.keys(o.T.de).length);
