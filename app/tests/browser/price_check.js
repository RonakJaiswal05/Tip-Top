// Paste into the console on /de/ (LANG "de") or /en/ (LANG "en"). See README.md.
(async (LANG = document.documentElement.lang) => {
  const E = (await fetch("/static/test/expected_labels.json").then(r => r.json()))[LANG];
  const H = LANG === "de" ? "rechner" : "calculator", sleep = ms => new Promise(r => setTimeout(r, ms));
  let checked = 0; const bad = [];
  for (const slug of Object.keys(E)) {
    location.hash = "#" + H + "=" + slug; await sleep(30);
    for (let i = 0; i < 20 && !document.querySelector(".rgrid"); i++) await sleep(20);
    const all = document.querySelector("[data-b=all]"); if (all) { all.click(); await sleep(10); }
    const got = {};
    document.querySelectorAll("#bldBody .rc").forEach(b => got[b.dataset.v] = b.querySelector("small").textContent);
    document.querySelectorAll("#bldBody .rlist button").forEach(b => got[b.dataset.v] = b.querySelector("span:last-child").textContent);
    for (const [k, v] of Object.entries(E[slug])) { checked++; if (got[k] !== v) bad.push([slug, k, got[k], v]); }
  }
  console.log({ models: Object.keys(E).length, checked, mismatches: bad.length, sample: bad.slice(0, 10) });
})();
