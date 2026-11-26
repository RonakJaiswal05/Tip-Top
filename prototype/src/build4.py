import os, re, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run from anywhere
s = open('src3.html', encoding='utf-8').read()
css = open('style4.css', encoding='utf-8').read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f"MISMATCH ({n}) for: {old[:90]!r}")
    s = s.replace(old, new)

# ---- head ----
s = re.sub(r'<style>.*?</style>', '<style>\n' + css.replace('\\', '\\\\') + '\n</style>', s, count=1, flags=re.S)
rep('<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wdth,wght@12..96,75..100,300..800&family=Hanken+Grotesk:wght@400..700&display=swap" rel="stylesheet">',
    '<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap" rel="stylesheet">')

# ---- nav ----
rep('''<svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="19" fill="#C8A268"/><circle cx="20" cy="20" r="14.5" fill="none" stroke="#16130F" stroke-width="1.2"/><text x="20" y="25" text-anchor="middle" fill="#16130F" style="font:700 13px 'Bricolage Grotesque',Arial,sans-serif">TT</text></svg>
    <b>TipTop <span style="font-weight:500;color:var(--muted)">Service 24</span></b>''',
    '''<svg viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="10" fill="#3048F0"/><text x="20" y="26.6" text-anchor="middle" fill="#fff" style="font:800 16px Archivo,Arial,sans-serif;font-stretch:118%">TT</text><circle cx="32.5" cy="7.5" r="3.2" fill="#FFE14D"/></svg>
    <b>TipTop <span>Service 24</span></b>''')
rep('''<button type="button" class="cta" data-open-builder><span class="dot" aria-hidden="true"></span><span data-t="cta"></span></button>
</header>''', '''<button type="button" class="cta" data-open-builder><span data-t="cta"></span></button>
  <span class="prog" aria-hidden="true"></span>
</header>''')

# ---- hero ----
CRACK = ('<svg class="crack" viewBox="0 0 100 20" preserveAspectRatio="none" aria-hidden="true">'
  '<path pathLength="1" style="--i:0" d="M89 10.5 L81 8.5 L72 9.5 L61 6.5 L50 8 L40 4.5 L29 6 L19 3.5"/>'
  '<path pathLength="1" style="--i:1" d="M89 10.5 L80 13.5 L71 12.5 L59 15.5 L47 14 L36 17 L23 15.5 L11 18.5"/>'
  '<path pathLength="1" style="--i:2" d="M89 10.5 L85 6 L79 3 L75 -1.5"/>'
  '<path pathLength="1" style="--i:3" d="M89 10.5 L93 15 L91 20.5"/>'
  '<path pathLength="1" style="--i:4" d="M89 10.5 L97 8 L104 9"/>'
  '<path pathLength="1" style="--i:5" d="M89 10.5 L83 17 L78 21.5"/>'
  '<path class="thin" pathLength="1" style="--i:6" d="M61 6.5 L57 1.5"/>'
  '<path class="thin" pathLength="1" style="--i:7" d="M47 14 L44 20"/>'
  '<path class="thin" pathLength="1" style="--i:8" d="M72 9.5 L69 14.5"/>'
  '<path class="thin" pathLength="1" style="--i:9" d="M40 4.5 L35 0"/>'
  '<path class="thin" pathLength="1" style="--i:10" d="M59 15.5 L61 21"/>'
  '<path class="thin" pathLength="1" style="--i:11" d="M86 9.5 L88 8.5 L91 9 L92 10.5 L90 12 L87 11.5 Z"/>'
  '</svg>')
rep('<h1><span class="ln"><span data-t="h1a"></span></span><span class="ln"><span data-t="h1b"></span></span></h1>',
    '<h1><span class="l1"><span data-t="h1a"></span>' + CRACK + '</span><span class="l2" data-t="h1b"></span></h1>')

# ---- repairs ----
rep('''    <div class="wrap head">
      <h2 data-t="pop_h"></h2>
      <div class="row" style="gap:24px;align-items:flex-end"><p data-t="pop_p"></p>
      <div class="arrows"><button type="button" id="railL" data-ta="prev"></button><button type="button" id="railR" data-ta="next"></button></div></div>
    </div>
    <div class="rail" id="rail"></div>''',
'''    <div class="wrap">
      <div class="head"><h2 data-rv><span class="rv-line"><span data-t="pop_h"></span></span></h2><p data-t="pop_p"></p></div>
      <div class="reps" id="rail"></div>
    </div>''')

# ---- brands ----
rep('''  <section class="brandsec" id="brands">
    <div class="wrap head"><h2 data-t="br_h"></h2><p data-t="br_p"></p></div>
    <div class="wrap bw" id="brandWall"></div>
  </section>''',
'''  <section class="sec fog" id="brands">
    <div class="wrap">
      <div class="head"><h2 data-rv><span class="rv-line"><span data-t="br_h"></span></span></h2><p data-t="br_p"></p></div>
      <div class="cab" id="brandWall"></div>
    </div>
  </section>''')

# ---- before/after ----
rep('''      <div class="head"><h2 data-t="cmp_h"></h2><p data-t="cmp_p"></p></div>''',
    '''      <div class="head"><h2 data-rv><span class="rv-line"><span data-t="cmp_h"></span></span></h2><p data-t="cmp_p"></p></div>''')

# ---- workshop ----
rep('''  <section class="lab" id="workshop">
    <div class="lab-sticky">
      <div class="wrap head"><h2 data-t="lab_h"></h2><p data-t="lab_p"></p></div>
      <div class="lab-track" id="labTrack"></div>
    </div>
  </section>''',
'''  <section class="wks" id="workshop">
    <div class="wrap">
      <div class="head"><h2 data-rv><span class="rv-line"><span data-t="lab_h"></span></span></h2><p data-t="lab_p"></p></div>
      <div class="lgrid" id="labTrack"></div>
      <p class="lab-note" id="labNote"></p>
    </div>
  </section>''')

# ---- sell / shops / faq heads ----
rep('<h2 class="big" data-t="sell_h"></h2>', '<h2 class="big" data-rv><span class="rv-line"><span data-t="sell_h"></span></span></h2>')
rep('<div class="head"><h2 data-t="shops_h"></h2><p data-t="shops_p"></p></div>', '<div class="head"><h2 data-rv><span class="rv-line"><span data-t="shops_h"></span></span></h2><p data-t="shops_p"></p></div>')
rep('<h2 class="big" data-t="faq_h"></h2>', '<h2 class="big" data-rv><span class="rv-line"><span data-t="faq_h"></span></span></h2>')
rep('<section class="sec" id="shops" style="padding-top:0">', '<section class="sec" id="shops">')

# ---- copy (EN) ----
rep('h1a:"Broken today.", h1b:"Fixed today.",', 'h1a:"Phone broken?", h1b:"We fix it while you wait.",')
rep('hero_p:"TipTop Service 24 repairs phones, tablets, laptops and consoles in Berlin-Moabit and Spandau. Most repairs take under an hour.",',
    'hero_p:"TipTop Service 24 repairs smartphones, tablets, laptops and consoles in Berlin-Moabit and Spandau. Most repairs take less than an hour, no appointment needed.", stk_hero:"Screens from",')
rep('br_h:"Every brand. One workshop.", br_p:"Tap a brand to see its models and prices.",', 'br_h:"Brands we repair", br_p:"Open a drawer to see that brand\'s models and prices.",')
rep('facts:["Most repairs in under an hour","Up to 24 months warranty","No appointment needed"],', 'facts:["Up to 24 months warranty","Premium or original parts","Free pickup within 5 km"],')
rep('pop_h:"What\'s broken?", pop_p:"Tap a repair, pick your model and see your price.",', 'pop_h:"Repairs and prices", pop_p:"Smartphone prices shown. Tap a repair, pick your model and see the exact price.",')
rep('cmp_h:"Same phone. Same day.",', 'cmp_h:"Before and after",')
rep('lab_h:"Board-level repairs in our own workshop.",', 'lab_h:"Our own workshop for the hard cases",')
rep('lab_end_h:"Since 2009 in Moabit.", lab_end_p:"More than 15,000 customers. Certified workshop. Parts in original quality.",', 'lab_note:"More than {n} customers since 2009 in Moabit, with parts in original quality.",')
rep('sell_h:"Sell your old device.",', 'sell_h:"Sell your old device",')
rep('shops_h:"Come by.",', 'shops_h:"Two shops in Berlin",')
rep('faq_h:"Good to know.",', 'faq_h:"Questions",')
rep('lf_h:"Repair request.",', 'lf_h:"Repair request",')
# ---- copy (DE) ----
rep('h1a:"Heute kaputt.", h1b:"Heute repariert.",', 'h1a:"Handy kaputt?", h1b:"Wir reparieren, während du wartest.",')
rep('hero_p:"TipTop Service 24 repariert Handys, Tablets, Laptops und Konsolen in Berlin-Moabit und Spandau. Die meisten Reparaturen dauern unter einer Stunde.",',
    'hero_p:"TipTop Service 24 repariert Smartphones, Tablets, Laptops und Konsolen in Berlin-Moabit und Spandau. Die meisten Reparaturen dauern weniger als eine Stunde, ohne Termin.", stk_hero:"Displays ab",')
rep('br_h:"Jede Marke. Eine Werkstatt.", br_p:"Marke antippen, Modelle und Preise sehen.",', 'br_h:"Diese Marken reparieren wir", br_p:"Schublade öffnen und Modelle und Preise der Marke sehen.",')
rep('facts:["Meist in unter einer Stunde","Bis zu 24 Monate Garantie","Ohne Termin"],', 'facts:["Bis zu 24 Monate Garantie","Premium- oder Originalteile","Kostenlose Abholung im Umkreis von 5 km"],')
rep('pop_h:"Was ist kaputt?", pop_p:"Reparatur antippen, Modell wählen, Preis sehen.",', 'pop_h:"Reparaturen und Preise", pop_p:"Gezeigt sind Smartphone-Preise. Reparatur antippen, Modell wählen, genauen Preis sehen.",')
rep('cmp_h:"Gleiches Handy. Gleicher Tag.",', 'cmp_h:"Vorher und nachher",')
rep('lab_h:"Platinen-Reparatur in der eigenen Werkstatt.",', 'lab_h:"Eigene Werkstatt für die schweren Fälle",')
rep('lab_end_h:"Seit 2009 in Moabit.", lab_end_p:"Mehr als 15.000 Kunden. Zertifizierte Werkstatt. Teile in Originalqualität.",', 'lab_note:"Mehr als {n} Kunden seit 2009 in Moabit, mit Teilen in Originalqualität.",')
rep('sell_h:"Verkauf dein altes Gerät.",', 'sell_h:"Verkauf dein altes Gerät",')
rep('shops_h:"Komm vorbei.",', 'shops_h:"Zwei Filialen in Berlin",')
rep('faq_h:"Gut zu wissen.",', 'faq_h:"Häufige Fragen",')
rep('lf_h:"Reparatur­anfrage.",', 'lf_h:"Reparatur­anfrage",')

# ---- image prompts ----
i0 = s.index('const STYLE = '); i1 = s.index('IMGS.forEach((m, i) =>')
s = s[:i0] + open('imgs4.js', encoding='utf-8').read() + '\n' + s[i1:]

# ---- device tiles ----
rep('''  return CATS.map(c => `<button type="button" class="dev" ${attr}="${c}">${ph(CAT_IMG[c])}<b>${esc(t("cat_" + c))}</b><small>${esc(t("cat_" + c + "_s"))}</small></button>`).join("");''',
    '''  return CATS.map(c => `<button type="button" class="dev" ${attr}="${c}" style="--cc:var(--c-${c})"><span class="tile">${ph(CAT_IMG[c], "notag")}</span><b>${esc(t("cat_" + c))}${ic("right", 2.4)}</b><small>${esc(t("cat_" + c + "_s"))}</small></button>`).join("");''')

# ---- builder colour + total bump ----
rep('''  $("bldBack").disabled = B.step === 1 || !!B.done;''', '''  $("bldBack").disabled = B.step === 1 || !!B.done;
  $("bldPanel").style.setProperty("--cc", B.cat ? "var(--c-" + B.cat + ")" : "var(--ink)");''')
rep('''  renderSide(); hydrate($("bldBody"));''', '''  renderSide(); hydrate($("bldBody"));
  const tb = $("bTotal"); if (tb) { if (ANIM && B._tot && B._tot !== tb.textContent) tb.classList.add("bump"); B._tot = tb.textContent; } else B._tot = null;
  if (!$("bld").hidden && (document.activeElement === document.body || !document.activeElement || !$("bld").contains(document.activeElement))) $("bldPanel").focus({ preventScroll:true });''')

# ---- page sections ----
i0 = s.index('function renderHero() {'); i1 = s.index('const SELL = { cat:"phone", cond:1 };')
s = s[:i0] + open('sections4.js', encoding='utf-8').read() + '\n' + s[i1:]
rep('''  $("sellMedia").innerHTML = ph("sell");''', '''  if (!$("sellMedia").firstChild || $("sellMedia").dataset.l !== lang) { $("sellMedia").innerHTML = `<div class="fr wipe">${ph("sell", "notag")}</div>`; $("sellMedia").dataset.l = lang; watch($("sellMedia")); }''')
rep('''  $("sellTicks").innerHTML = t("sell_ticks").map(x => `<li>${esc(x)}</li>`).join("");''', '''  $("sellTicks").innerHTML = t("sell_ticks").map(x => `<li>${ic("check", 2.4)}<span>${esc(x)}</span></li>`).join("");''')
i0 = s.index('function renderShops() {'); i1 = s.index('const BRANDWALL = [')
s = s[:i0] + open('shops4.js', encoding='utf-8').read() + '\n' + s[i1:]
i0 = s.index('function renderBrands() {'); i1 = s.index('$("brandWall").addEventListener("click"')
s = s[:i0] + open('brands4.js', encoding='utf-8').read() + '\n' + s[i1:]
rep('''$("railL").addEventListener("click", () => $("rail").scrollBy({ left:-$("rail").clientWidth * .7, behavior:"smooth" }));
$("railR").addEventListener("click", () => $("rail").scrollBy({ left:$("rail").clientWidth * .7, behavior:"smooth" }));''', '')

# ---- before/after: expose setter, stop sweep on touch ----
rep('''  cmp.addEventListener("pointerdown", ev => { drag = true; cmp.setPointerCapture(ev.pointerId); at(ev); });''',
    '''  cmpSet = set;
  cmp.addEventListener("pointerdown", ev => { cmp.dataset.touched = "1"; drag = true; cmp.setPointerCapture(ev.pointerId); at(ev); });''')
rep('''  cmp.addEventListener("keydown", ev => { const x''', '''  cmp.addEventListener("keydown", ev => { cmp.dataset.touched = "1"; const x''')

# ---- remove pinned gallery ----
i0 = s.index('/* Pinned horizontal workshop gallery */'); i1 = s.index('/* ===== Image prompt drawer ===== */')
s = s[:i0] + open('motion4.js', encoding='utf-8').read() + '\n' + s[i1:]

# motion helpers must exist before first render: define ANIM early
rep('''const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;''',
    '''const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const ANIM = !reduce;
if (ANIM) document.documentElement.classList.add("anim");
let cmpSet = () => {};''')

rep('  hydrate(); requestAnimationFrame(setupLab);', '  hydrate(); watch(document); requestAnimationFrame(setupLab);')
exec(open('patch_dev.py', encoding='utf-8').read())
exec(open('patch_legal.py', encoding='utf-8').read())
exec(open('patch_gmb.py', encoding='utf-8').read())
exec(open('patch_feedback.py', encoding='utf-8').read())  # client feedback 17 Nov 2026
exec(open('patch_nov17.py', encoding='utf-8').read())  # client voice note 17 Nov 2026 evening
exec(open('patch_nov26.py', encoding='utf-8').read())  # call with the owner, 25 Nov 2026
exec(open('patch_hero_video.py', encoding='utf-8').read())  # desktop hero film, softer call text, 26 Nov 2026
open('src4.html', 'w', encoding='utf-8').write(s)
print("ok", len(s))
