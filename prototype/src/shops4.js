function renderShops() {
  const st = openStatus();
  $("shopList").innerHTML = SHOPS.map(sh => `<article class="shop">
    <div class="fr"><div class="sign" aria-hidden="true"><span><small>${esc(sh.area.replace("Berlin-", ""))}</small><b>${esc(sh.street)}</b></span></div>${ph(sh.id, "notag")}
      <span class="tag-open shop-open"><span class="pulse${st.open ? "" : " off"}"></span>${esc(st.text)}</span></div>
    <div class="shop-b">
      <p class="shop-k">${ic("store", 1.9)}${esc(sh.area)}</p>
      <h3>${esc(sh.street)}</h3>
      <p class="addr">${esc(sh.zip)}</p>
      ${gmbShop(sh.g)}
      <p class="shop-h">${ic("clock", 1.9)}<span>${esc(t("f_hours"))}</span></p>
      <div class="shop-acts"><a class="btn" href="${mapsUrl(sh)}" target="_blank" rel="noopener">${ic("store")}${esc(t("directions"))}</a><a class="btn line" href="tel:${sh.tel}">${ic("call")}${esc(sh.telTxt)}</a></div>
    </div></article>`).join("");
  const w = t("ways");
  $("ways").innerHTML = `<div class="way w1"><span class="wi">${ic("store", 1.8)}</span><div><b>${esc(w[0][0])}</b><p>${esc(w[0][1])}</p></div></div>
    <a class="way w2" href="${waLink(t("wa_pick"))}" target="_blank" rel="noopener"><span class="wi">${ic("wa", 1.9)}</span><div><b>${esc(w[1][0])}</b><p>${esc(w[1][1])}</p><span class="wgo">${esc(w[1][2])}${ic("right", 2.4)}</span></div></a>
    <button type="button" class="way w3" id="copyAddr"><span class="wi">${ic("ship", 1.8)}</span><div><b>${esc(w[2][0])}</b><p>${esc(w[2][1])}</p><span class="wgo">${esc(w[2][2])}${ic("right", 2.4)}</span></div></button>`;
  $("copyAddr").onclick = () => copyText("TipTop Service 24, Beusselstraße 18, 10553 Berlin", t("copied"));
}
