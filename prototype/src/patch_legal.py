# Legal compliance layer: legal pages, cookie consent, withdrawal function, self-hosted fonts, form notices.
# exec'd from build4.py after patch_dev.py, operating on the global string `s` with rep().

# ---- head: self-hosted fonts, no Google Fonts ----
rep('''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap" rel="stylesheet">''',
'''<meta name="description" content="TipTop Service 24: Handy-, Tablet-, Laptop- und Konsolenreparatur in Berlin-Moabit und Spandau. Preis in Sekunden, Reparatur meist in unter einer Stunde.">
<link rel="preload" href="fonts/archivo-latin.woff2" as="font" type="font/woff2" crossorigin>''')
rep('</style>', open('legal4.css', encoding='utf-8').read().replace('\\', '\\\\') + '\n</style>')

# ---- footer ----
rep('''          <li><a href="https://www.instagram.com/tiptopservice24/" target="_blank" rel="noopener">Instagram</a></li>
          <li><a href="https://tiptophandyreparatur.de/policies/legal-notice" target="_blank" rel="noopener" data-t="f_imp"></a></li>
          <li><a href="https://tiptophandyreparatur.de/policies/privacy-policy" target="_blank" rel="noopener" data-t="f_priv"></a></li>
          <li><a href="#admin">Admin</a></li>
          <li><button type="button" id="imgLink" style="color:inherit;font:inherit;padding:0" data-t="img_btn"></button></li>
        </ul></div>
      </div>
      <div class="fbase"><span>© 2026 TipTop Service 24</span><span data-t="proto_foot"></span></div>''',
'''          <li><a href="https://www.instagram.com/tiptopservice24/" target="_blank" rel="noopener">Instagram</a></li>
          <li><a href="#admin">Admin</a></li>
          <li><button type="button" id="imgLink" style="color:inherit;font:inherit;padding:0" data-t="img_btn"></button></li>
        </ul></div>
        <div><h4 data-t="f_legal"></h4><ul>
          <li><a href="#impressum" data-t="f_imp"></a></li>
          <li><a href="#datenschutz" data-t="f_priv"></a></li>
          <li><a href="#agb" data-t="f_agb"></a></li>
          <li><a href="#widerruf" data-t="f_wdr_i"></a></li>
          <li><a href="#cookies" data-t="f_ck"></a></li>
          <li><a href="#barrierefreiheit" data-t="f_a11y"></a></li>
          <li><button type="button" data-ccopen style="color:inherit;font:inherit;padding:0" data-t="f_ccset"></button></li>
        </ul></div>
      </div>
      <div class="fbase"><span>© 2026 TLAMO GmbH, TipTop Service 24</span><a class="fwd" href="#vertrag-widerrufen" data-t="f_wdr"></a><span data-t="proto_foot"></span></div>''')

# ---- legal view, banner and dialogs ----
rep('<main id="v-admin" class="adminv" hidden><div class="wrap" id="adminBody"></div></main>',
'''<main id="v-admin" class="adminv" hidden><div class="wrap" id="adminBody"></div></main>

<!-- ================= LEGAL PAGES ================= -->
<main id="v-legal" class="legalv" hidden><div class="wrap lg" id="legalBody"></div></main>''')
rep('<a class="fab" id="fab" target="_blank" rel="noopener" aria-label="WhatsApp"></a>',
'''<!-- ================= COOKIE CONSENT ================= -->
<section class="cc" id="cc" aria-labelledby="ccH" hidden></section>
<div class="ccm" id="ccm" hidden><div class="bld-scrim" data-ccx></div><div class="ccm-p" id="ccmP" role="dialog" aria-modal="true" aria-labelledby="ccmH" tabindex="-1"></div></div>
<div class="ccm" id="micm" hidden><div class="bld-scrim" data-micx></div><div class="ccm-p sm" id="micP" role="dialog" aria-modal="true" aria-labelledby="micH" tabindex="-1"></div></div>

<a class="fab" id="fab" target="_blank" rel="noopener" aria-label="WhatsApp"></a>''')

# ---- form notices ----
rep('<p class="err" id="cbErr"></p><button type="submit" class="btn" style="justify-self:start">',
    '<p class="err" id="cbErr"></p><p class="fine">${fine("fine_cb")}</p><button type="submit" class="btn" style="justify-self:start">')
rep('</span></button>${wi}\n    </div>`;', '</span></button>${wi}\n    </div>\n    <p class="fine bfine">${fine("fine_wa")}</p>`;')
rep('<p class="err" id="lfErr"></p><button type="submit"', '<p class="err" id="lfErr"></p><p class="fine">${fine("fine_lf")}</p><button type="submit"')
rep('<a class="btn-wa" id="sellWa" target="_blank" rel="noopener"></a>', '<a class="btn-wa" id="sellWa" target="_blank" rel="noopener"></a>\n          <p class="fine" id="sellFine"></p>')
rep('''  $("sellWa").innerHTML = ic("wa", 1.9) + `<span>${esc(t("sell_btn"))}</span>`;''',
    '''  $("sellWa").innerHTML = ic("wa", 1.9) + `<span>${esc(t("sell_btn"))}</span>`;
  $("sellFine").innerHTML = fine("fine_sell");''')

# ---- voice input goes through the notice first ----
rep('$("askMic").addEventListener("click", () => startVoice(', '$("askMic").addEventListener("click", () => voiceGate(')
rep('$("lfMic").addEventListener("click", () => startVoice(', '$("lfMic").addEventListener("click", () => voiceGate(')

# ---- JS modules ----
LEGAL_JS = '\n'.join(open(f, encoding='utf-8').read() for f in ['legal_h.js', 'legal_de.js', 'legal_en.js', 'legal4.js'])
rep('/* ===== Language, routing, boot ===== */', LEGAL_JS + '\n/* ===== Language, routing, boot ===== */')

rep('''  if (!$("v-admin").hidden) renderAdmin();
  hydrate(); watch(document); requestAnimationFrame(setupLab);''',
'''  if (!$("v-admin").hidden) renderAdmin();
  if (!$("v-legal").hidden) renderLegal();
  renderCC();
  hydrate(); watch(document); requestAnimationFrame(setupLab);''')

rep('''  const view = h === "anfrage" ? "lead" : h === "admin" ? "admin" : "site";
  const wasHidden = $("v-site").hidden;
  $("v-site").hidden = view !== "site"; $("v-lead").hidden = view !== "lead"; $("v-admin").hidden = view !== "admin";
  $("fab").hidden = view === "admin";
  if (view === "lead") { renderLead(); scrollTo(0, 0); }
  else if (view === "admin") { renderAdmin(); scrollTo(0, 0); }''',
'''  const lg = h === "vertrag-widerrufen" ? "widerruf" : LEGAL_KEYS.includes(h) ? h : null;
  const view = h === "anfrage" ? "lead" : h === "admin" ? "admin" : lg ? "legal" : "site";
  const wasHidden = $("v-site").hidden;
  if (view !== "site" && !$("bld").hidden) closeBuilder();
  closeCCM(); closeMic();
  $("v-site").hidden = view !== "site"; $("v-lead").hidden = view !== "lead"; $("v-admin").hidden = view !== "admin"; $("v-legal").hidden = view !== "legal";
  $("fab").hidden = view === "admin";
  if (view !== "legal") document.title = TITLE0;
  renderCC();
  if (view === "lead") { renderLead(); scrollTo(0, 0); }
  else if (view === "admin") { renderAdmin(); scrollTo(0, 0); }
  else if (view === "legal") {
    if (h === "vertrag-widerrufen" && !WD.done) WD.open = true;
    renderLegal(lg); scrollTo({ top:0, behavior:"instant" });
    if (h === "vertrag-widerrufen") requestAnimationFrame(() => { const w = $("wd"), n = $("wdN"); if (w) w.scrollIntoView({ block:"center", behavior:"instant" }); if (n) n.focus({ preventScroll:true }); });
  }''')
rep('''buildModels();
applyLang();
route();''', '''buildModels();
ccApply();
applyLang();
route();''')
