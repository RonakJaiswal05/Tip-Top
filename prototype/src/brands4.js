/* Brand logos: drop the official SVG files into img/brands/<slug>.svg and add the slug to BRAND_LOGOS_READY.
   Live site: each brand has a logo upload field in the admin. Until a logo is there, the drawer shows the name only. */
const BRAND_LOGO = { "Apple":"apple", "iPad":"apple", "MacBook":"apple", "Samsung":"samsung", "Galaxy Tab":"samsung", "Google Pixel":"google", "Xiaomi":"xiaomi",
  "Huawei":"huawei", "Huawei MateBook":"huawei", "OnePlus":"oneplus", "Oppo":"oppo", "Sony Xperia":"sony", "Motorola":"motorola", "Lenovo":"lenovo", "HP":"hp",
  "Dell":"dell", "ASUS":"asus", "Acer":"acer", "Microsoft Surface":"microsoft", "MSI":"msi", "PlayStation":"playstation", "DualSense":"playstation",
  "Xbox":"xbox", "Nintendo Switch":"nintendo", "Joy-Con":"nintendo", "Steam Deck":"steam" };
// Logo files supplied by Ronak on 17 Nov 2026 (single-colour SVGs, viewBox cropped to the mark, ink #12141C).
const BRAND_LOGOS_READY = new Set(["apple","samsung","google","xiaomi","huawei","oneplus","oppo","sony","motorola","lenovo","hp","dell","asus","acer","microsoft","msi","playstation","xbox","nintendo","steam"]);
// Wordmarks already spell the brand, so the drawer drops the repeated brand word ("Sony Xperia" -> [SONY] Xperia).
const BRAND_WORDMARK = { samsung:"Samsung", sony:"Sony", lenovo:"Lenovo", asus:"ASUS", acer:"Acer", msi:"MSI", oppo:"Oppo" };
function drwLabel(nm) {
  const lg = BRAND_LOGO[nm];
  if (!lg || !BRAND_LOGOS_READY.has(lg)) return `<span class="lbl">${esc(nm)}</span>`;
  const wm = BRAND_WORDMARK[lg];
  let txt = nm;
  if (wm && nm.toLowerCase().startsWith(wm.toLowerCase())) txt = nm.slice(wm.length).trim();
  const img = `<img class="blogo lg-${lg}${wm ? " wm" : ""}" src="${(window.__BRANDDATA && window.__BRANDDATA[lg]) || "img/brands/" + lg + ".svg"}" alt="" aria-hidden="true">`;
  return `<span class="lbl has-logo${txt ? "" : " only"}">${img}${txt ? `<span>${esc(txt)}</span>` : ""}${txt === nm ? "" : `<span class="sr">${esc(nm)}</span>`}</span>`;
}
function renderBrands() {
  const G = { br_phone:"phone", br_laptop:"laptop", br_console:"console" };
  $("brandWall").innerHTML = BRANDWALL.map(([lab, items]) => {
    const g = G[lab];
    return `<div class="cab-g" style="--cc:var(--c-${g});--tc:var(--t-${g})"><h3><i aria-hidden="true"></i>${esc(t(lab))}</h3><div class="drawers">` +
      items.map(([nm, ca, b], i) => `<button type="button" class="drw wait" data-bc="${ca}" data-bb="${esc(b)}" style="--d:${(i * .04).toFixed(2)}s${ca !== g ? `;--cc:var(--c-${ca});--tc:var(--t-${ca})` : ""}">${drwLabel(nm)}<span class="pull" aria-hidden="true"></span></button>`).join("") +
      `</div></div>`;
  }).join("");
  watch($("brandWall"));
}
