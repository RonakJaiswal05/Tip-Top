/* ===== Admin preview ===== */
const AD = { in:false, tab:0, cat:"phone", q:"", sel:null, nb:{ cat:"phone", lvl:1, faceid:true, kind:0 } };
const LVL = [0.6, 1, 1.6, 2.2];
function renderAdmin() {
  const b = $("adminBody");
  if (!AD.in) {
    b.innerHTML = `<form class="acard login" id="adLogin" novalidate><h1>${esc(t("ad_title"))}</h1>
      <div><label class="lab" for="adU">${esc(t("ad_user"))}</label><input class="lin" id="adU" autocomplete="username"></div>
      <div><label class="lab" for="adP">${esc(t("ad_pass"))}</label><input class="lin" id="adP" type="password" autocomplete="current-password"></div>
      <button class="btn-dark" type="submit" style="justify-content:center">${esc(t("ad_sign"))}</button><p class="small">${esc(t("ad_demo"))}</p></form>`;
    $("adLogin").addEventListener("submit", e => { e.preventDefault(); AD.in = true; renderAdmin(); });
    return;
  }
  const tabs = t("ad_tabs").map((x, i) => `<button type="button" data-tab="${i}" aria-pressed="${AD.tab === i}">${esc(x)}${i === 2 && REQS.length ? ` (${REQS.length})` : ""}</button>`).join("");
  let body = "";
  if (AD.tab === 0) body = adPrices();
  else if (AD.tab === 1) body = adAdd();
  else body = adReqs();
  b.innerHTML = `<div class="abar"><h1>${esc(t("ad_title"))}</h1><div class="atabs" id="adTabs">${tabs}</div><div class="row" style="margin:0"><a class="btn-plain" href="#repair">${esc(t("ad_site"))}</a><button type="button" class="btn-plain" id="adOut">${esc(t("ad_out"))}</button></div></div>${body}`;
  $("adTabs").addEventListener("click", e => { const x = e.target.closest("button"); if (!x) return; AD.tab = +x.dataset.tab; renderAdmin(); });
  $("adOut").addEventListener("click", () => { AD.in = false; renderAdmin(); });
  if (AD.tab === 0) wirePrices(); else if (AD.tab === 1) wireAdd();
}
function adPrices() {
  const q = norm(AD.q).trim();
  const list = MODELS[AD.cat].filter(m => !q || norm(m.brand + " " + m.name).includes(q));
  const left = `<div class="acard"><div class="seg" id="adCat">${CATS.map(c => `<button type="button" data-v="${c}" aria-pressed="${AD.cat === c}">${esc(t("cat_" + c))}</button>`).join("")}</div>
    <input class="lin" id="adQ" style="margin-top:12px" placeholder="${esc(t("ad_search"))}" aria-label="${esc(t("ad_search"))}" value="${esc(AD.q)}">
    <div class="alist" id="adList">${list.map(m => `<button type="button" data-id="${m.id}" aria-pressed="${AD.sel === m.id}">${esc(locName(m.name))} <small>${esc(m.brand)}</small></button>`).join("")}</div></div>`;
  const m = AD.sel && MODELS[AD.cat].find(x => x.id === AD.sel);
  let right;
  if (!m) right = `<div class="acard"><p class="small">${esc(t("ad_pick"))}</p></div>`;
  else {
    const rows = [...servicesFor(m), "diagnosis"].map(k => {
      if (k === "display") return ["p", "o"].map(tr => `<tr><td>${esc(svName(k, m.cat))} <span class="badge">${esc(t(tr === "o" ? "q_o" : "q_p"))}</span></td><td><input type="number" min="0" step="1" data-k="${k}" data-tier="${tr}" value="${price(m, k, tr)}" data-def="${price(m, k, tr, true)}" aria-label="${esc(svName(k, m.cat) + " " + t(tr === "o" ? "q_o" : "q_p"))}"></td></tr>`).join("");
      return `<tr><td>${esc(svName(k, m.cat))}</td><td><input type="number" min="0" step="1" data-k="${k}" value="${price(m, k) == null ? "" : price(m, k)}" data-def="${price(m, k, null, true) == null ? "" : price(m, k, null, true)}" aria-label="${esc(svName(k, m.cat))}"></td></tr>`;
    }).join("");
    right = `<div class="acard"><h2 style="font-stretch:112%;font-size:22px">${esc(fullName(m))}</h2><div class="tablewrap"><table class="ptable" id="adTable"><thead><tr><th>${esc(t("ad_rep"))}</th><th>${esc(t("ad_price"))}</th></tr></thead><tbody>${rows}</tbody></table></div>
      <div class="abtns"><button type="button" class="btn-dark" id="adSave">${esc(t("ad_save"))}</button><button type="button" class="btn-plain" id="adReset">${esc(t("ad_reset"))}</button></div></div>`;
  }
  return `<div class="agrid">${left}${right}</div>`;
}
function wirePrices() {
  $("adCat").addEventListener("click", e => { const x = e.target.closest("button"); if (!x) return; AD.cat = x.dataset.v; AD.sel = null; AD.q = ""; renderAdmin(); });
  $("adQ").addEventListener("input", e => { AD.q = e.target.value; const pos = e.target.selectionStart; renderAdmin(); const i = $("adQ"); i.focus(); i.setSelectionRange(pos, pos); });
  $("adList").addEventListener("click", e => { const x = e.target.closest("button"); if (!x) return; AD.sel = x.dataset.id; renderAdmin(); });
  const tb = $("adTable"); if (!tb) return;
  tb.addEventListener("input", e => { const i = e.target; i.classList.toggle("chg", i.value !== i.dataset.def); });
  $("adSave").addEventListener("click", () => {
    tb.querySelectorAll("input").forEach(i => {
      const key = AD.sel + "|" + i.dataset.k + (i.dataset.tier ? "|" + i.dataset.tier : "");
      if (i.value === "" || i.value === i.dataset.def) delete OVR[key]; else OVR[key] = Math.max(0, Math.round(+i.value));
    });
    LS.set("tt-ovr", OVR); toast(t("ad_saved")); renderAdmin(); render();
  });
  $("adReset").addEventListener("click", () => { Object.keys(OVR).forEach(k => { if (k.startsWith(AD.sel + "|")) delete OVR[k]; }); LS.set("tt-ovr", OVR); toast(t("ad_resetd")); renderAdmin(); render(); });
}
function adAdd() {
  const nb = AD.nb;
  const brands = brandsOf(nb.cat);
  return `<form class="acard" id="adAddF" style="max-width:640px;display:grid;gap:16px" novalidate>
    <div><span class="lab">${esc(t("ad_cat"))}</span><div class="seg" id="nbCat">${CATS.map(c => `<button type="button" data-v="${c}" aria-pressed="${nb.cat === c}">${esc(t("cat_" + c))}</button>`).join("")}</div></div>
    <div class="two"><div><label class="lab" for="nbBrand">${esc(t("ad_brand"))}</label><input class="lin" id="nbBrand" list="nbBrands"><datalist id="nbBrands">${brands.map(x => `<option value="${esc(x)}">`).join("")}</datalist></div>
    <div><label class="lab" for="nbName">${esc(t("ad_name"))}</label><input class="lin" id="nbName"></div></div>
    <div><span class="lab">${esc(t("ad_level"))}</span><div class="seg" id="nbLvl">${t("levels").map((x, i) => `<button type="button" data-v="${i}" aria-pressed="${nb.lvl === i}">${esc(x)}</button>`).join("")}</div></div>
    ${nb.cat === "phone" ? `<label style="display:flex;gap:10px;align-items:center;font-weight:600"><input type="checkbox" id="nbFace" ${nb.faceid ? "checked" : ""} style="width:20px;height:20px">${esc(t("ad_faceid"))}</label>` : ""}
    ${nb.cat === "console" ? `<div><span class="lab">${esc(t("ad_kind"))}</span><div class="seg" id="nbKind">${t("kinds").map((x, i) => `<button type="button" data-v="${i}" aria-pressed="${nb.kind === i}">${esc(x)}</button>`).join("")}</div></div>` : ""}
    <p class="err" id="nbErr" style="color:#B3261E"></p>
    <button type="submit" class="btn-dark" style="justify-self:start">${esc(t("ad_add"))}</button></form>`;
}
function wireAdd() {
  const keepVals = () => ({ b:$("nbBrand").value, n:$("nbName").value });
  const restore = v => { $("nbBrand").value = v.b; $("nbName").value = v.n; };
  const seg = (id, fn) => { const el = $(id); if (el) el.addEventListener("click", e => { const x = e.target.closest("button"); if (!x) return; const v = keepVals(); fn(x.dataset.v); renderAdmin(); restore(v); }); };
  seg("nbCat", v => { AD.nb.cat = v; }); seg("nbLvl", v => { AD.nb.lvl = +v; }); seg("nbKind", v => { AD.nb.kind = +v; });
  const fc = $("nbFace"); if (fc) fc.addEventListener("change", () => { AD.nb.faceid = fc.checked; });
  $("adAddF").addEventListener("submit", e => {
    e.preventDefault();
    const brand = $("nbBrand").value.trim(), name = $("nbName").value.trim();
    if (!brand || !name) { $("nbErr").textContent = t("ad_err"); return; }
    let fl = "";
    if (AD.nb.cat === "phone" && AD.nb.faceid) fl += "F";
    if (AD.nb.cat === "console") fl += "BbHP"[AD.nb.kind];
    ADDED.push({ cat:AD.nb.cat, brand, name, f:LVL[AD.nb.lvl], fl });
    LS.set("tt-added", ADDED); buildModels();
    toast(t("ad_added", { m:brand + " " + name }));
    AD.tab = 0; AD.cat = AD.nb.cat; AD.sel = slug(AD.nb.cat + "-" + brand + "-" + name); renderAdmin();
  });
}
function adReqs() {
  if (!REQS.length) return `<div class="acard"><p class="small">${esc(t("ad_none"))}</p></div>`;
  const cols = t("ad_cols");
  const fmtD = iso => { try { return new Intl.DateTimeFormat(lang === "de" ? "de-DE" : "en-GB", { dateStyle:"short", timeStyle:"short", timeZone:"Europe/Berlin" }).format(new Date(iso)); } catch (e) { return iso; } };
  return `<div class="acard"><p class="small" style="margin-bottom:12px">${esc(t("ad_reqs_note"))}</p><div class="tablewrap"><table class="rtable"><thead><tr>${cols.map(c => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>
    ${REQS.map(r => `<tr><td class="num">${esc(fmtD(r.when))}</td><td>${esc(r.name)}</td><td class="num">${esc(r.phone)}</td><td>${esc(r.device)}</td><td>${esc(r.repair)}${r.total ? `<br><span class="small">${esc(r.total)}</span>` : ""}</td><td><span class="badge">${esc(r.via === "cb" ? t("via_cb") : r.via === "wd" ? t("via_wd") : t("via_form"))}</span>${r.contact ? `<br><span class="small">${esc(r.contact)}</span>` : ""}</td></tr>`).join("")}
  </tbody></table></div></div>`;
}

