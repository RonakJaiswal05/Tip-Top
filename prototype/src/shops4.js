function renderShops() {
  const st = openStatus();
  $("shopList").innerHTML = SHOPS.map(sh => `<article class="shop"><div class="fr"><div class="sign" aria-hidden="true"><span><small>${esc(sh.area.replace("Berlin-", ""))}</small><b>${esc(sh.street)}</b></span></div>${ph(sh.id, "notag")}</div><div class="shop-b"><h3>${esc(sh.area)}</h3><p class="addr">${esc(sh.street)}, ${esc(sh.zip)}</p>${gmbShop(sh.g)}<span class="stat"><span class="pulse${st.open ? "" : " off"}"></span>${esc(st.text)}</span>
    <div class="row" style="margin-top:8px"><a class="btn" href="${mapsUrl(sh)}" target="_blank" rel="noopener">${ic("store")}${esc(t("directions"))}</a><a class="btn line" href="tel:${sh.tel}">${ic("call")}${esc(sh.telTxt)}</a></div></div></article>`).join("");
  const w = t("ways");
  $("ways").innerHTML = `<div class="way"><b>${esc(w[0][0])}</b><p>${esc(w[0][1])}</p></div>
    <div class="way"><b>${esc(w[1][0])}</b><p>${esc(w[1][1])}</p><a href="${waLink(t("wa_pick"))}" target="_blank" rel="noopener">${esc(w[1][2])}</a></div>
    <div class="way"><b>${esc(w[2][0])}</b><p>${esc(w[2][1])}</p><button type="button" id="copyAddr">${esc(w[2][2])}</button></div>`;
  $("copyAddr").onclick = () => copyText("TipTop Service 24, Beusselstraße 18, 10553 Berlin", t("copied"));
}
