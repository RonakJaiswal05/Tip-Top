function sticker(small, big, style = "") {
  return `<span class="stk wait" style="${style}"><small>${esc(small)}</small><b>${esc(big)}</b></span>`;
}
function renderHero() {
  $("heroDevs").innerHTML = devTiles("data-hcat");
  const st = openStatus(), p = minPrice("phone", "display");
  $("heroMedia").innerHTML = `<div class="hero-frame">${ph("hero", "notag")}<span class="tag-open"><span class="pulse${st.open ? "" : " off"}"></span>${esc(st.text)}</span></div>` +
    (p != null ? sticker(t("stk_hero"), fmt(p), "--d:1.3s") : "");
  $("facts").innerHTML = t("facts").map(f => `<span>${ic("check", 2.4)}${esc(f)}</span>`).join("");
  $("askMic").innerHTML = ic("mic");
  watch($("heroMedia"));
}
const REP_ROT = [-9, 7, -5, 10, -12, 6];
function renderRail() {
  $("rail").innerHTML = TOP6.phone.map((k, i) => {
    const p = minPrice("phone", k);
    return `<button type="button" class="rep" data-rail="${k}"><span class="fr wipe" style="transition-delay:${(i % 3) * .08}s">${ph(REP_IMG[k], "notag")}</span>` +
      (p != null ? sticker(t("from"), fmt(p), `--d:${(.45 + (i % 3) * .12).toFixed(2)}s;--r:${REP_ROT[i]}deg`) : "") +
      `<span class="rep-cap"><b>${esc(svName(k, "phone"))}</b><span class="go2">${ic("right", 2.2)}</span></span></button>`;
  }).join("");
  watch($("rail"));
}
function renderCmp() {
  $("cmp").innerHTML = ph("before", "bef notag") + ph("after", "after notag") + `<span class="lbl b">${esc(t("before"))}</span><span class="lbl a">${esc(t("after"))}</span><span class="bar"></span><span class="knob" role="slider" tabindex="0" aria-label="${esc(t("cmp_h"))}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="50">${ic("lr", 2.2)}</span>`;
  watch($("cmp").parentNode);
}
function renderLab() {
  $("labTrack").innerHTML = t("lab").map(([h, p], i) => `<article class="lcard"><div class="fr wipe">${ph(["lab-solder","lab-ic","lab-water","lab-data"][i], "notag")}</div><h3>${esc(h)}</h3><p>${esc(p)}</p></article>`).join("");
  const n = new Intl.NumberFormat(lang === "de" ? "de-DE" : "en-IE").format(15000);
  $("labNote").innerHTML = esc(t("lab_note")).replace("{n}", `<b data-count="15000">${n}</b>`);
  watch($("workshop"));
}
