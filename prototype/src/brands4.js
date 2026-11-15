/* Brand logos: drop the official SVG files into img/brands/<slug>.svg and add the slug to BRAND_LOGOS_READY.
   Live site: each brand has a logo upload field in the admin. Until a logo is there, the drawer shows the name only. */
const BRAND_LOGO = { "Apple":"apple", "iPad":"apple", "MacBook":"apple", "Samsung":"samsung", "Galaxy Tab":"samsung", "Google Pixel":"google", "Xiaomi":"xiaomi",
  "Huawei":"huawei", "Huawei MateBook":"huawei", "OnePlus":"oneplus", "Oppo":"oppo", "Sony Xperia":"sony", "Motorola":"motorola", "Lenovo":"lenovo", "HP":"hp",
  "Dell":"dell", "ASUS":"asus", "Acer":"acer", "Microsoft Surface":"microsoft", "MSI":"msi", "PlayStation":"playstation", "DualSense":"playstation",
  "Xbox":"xbox", "Nintendo Switch":"nintendo", "Joy-Con":"nintendo", "Steam Deck":"steam" };
const BRAND_LOGOS_READY = new Set([]);
function renderBrands() {
  const G = { br_phone:"phone", br_laptop:"laptop", br_console:"console" };
  $("brandWall").innerHTML = BRANDWALL.map(([lab, items]) => {
    const g = G[lab];
    return `<div class="cab-g" style="--cc:var(--c-${g});--tc:var(--t-${g})"><h3><i aria-hidden="true"></i>${esc(t(lab))}</h3><div class="drawers">` +
      items.map(([nm, ca, b], i) => { const lg = BRAND_LOGO[nm], has = lg && BRAND_LOGOS_READY.has(lg); return `<button type="button" class="drw wait" data-bc="${ca}" data-bb="${esc(b)}" style="--d:${(i * .04).toFixed(2)}s${ca !== g ? `;--cc:var(--c-${ca});--tc:var(--t-${ca})` : ""}"><span class="lbl${has ? " has-logo" : ""}">${has ? `<img class="blogo" src="img/brands/${lg}.svg" alt="" aria-hidden="true">` : ""}${esc(nm)}</span><span class="pull" aria-hidden="true"></span></button>`; }).join("") +
      `</div></div>`;
  }).join("");
  watch($("brandWall"));
}
