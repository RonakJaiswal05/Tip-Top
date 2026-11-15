/* ===== Google ratings (Google Business Profile) =====
   Prototype: snapshot from Google Maps on 15 Nov 2026.
   Live site: fetched once a day from the Google Places API (Place Details: rating, userRatingCount) and shown with Google attribution. */
const GMB = {
  asof:"2026-11-15",
  moabit:{ r:4.9, n:321, pid:"ChIJA6sIHRNRqEcRdYbk2bTKeB4", q:"Meisterwerkstatt TipTop Service 24, Beusselstraße 18, 10553 Berlin", s:"Moabit" },
  spandau:{ r:4.0, n:44, pid:"ChIJk4noUUFWqEcR8pf5IuXJ-7U", q:"Tip Top Reparatur Service, Havelstraße 8, 13597 Berlin", s:"Spandau" }
};
Object.assign(T.en, { gmb_n:"{n} Google reviews, {s} shop", gmb_shop:"{n} Google reviews", gmb_aria:"Rated {r} out of 5", gmb_title:"Google rating as of {d}",
  br_tm:"All brand names and logos belong to their owners. TipTop Service 24 is an independent workshop and not an authorised service partner of the manufacturers." });
Object.assign(T.de, { gmb_n:"{n} Google-Bewertungen, Filiale {s}", gmb_shop:"{n} Google-Bewertungen", gmb_aria:"Bewertet mit {r} von 5", gmb_title:"Google-Bewertung, Stand {d}",
  br_tm:"Alle genannten Marken und Logos gehören ihren jeweiligen Inhabern. TipTop Service 24 ist eine unabhängige Werkstatt und kein autorisierter Servicepartner der Hersteller." });
const gmbUrl = g => "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(g.q) + "&query_place_id=" + g.pid;
const num1 = x => { try { return new Intl.NumberFormat(lang === "de" ? "de-DE" : "en-IE", { minimumFractionDigits:1, maximumFractionDigits:1 }).format(x); } catch (e) { return String(x); } };
const STAR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.6l2.9 6 6.5.8-4.8 4.5 1.2 6.5L12 17.3l-5.8 3.1 1.2-6.5L2.6 9.4l6.5-.8z"/></svg>';
function stars(r) {
  return `<span class="stars" role="img" aria-label="${esc(t("gmb_aria", { r:num1(r) }))}"><span class="s0">${STAR.repeat(5)}</span><span class="s1" style="width:${(r / 5 * 100).toFixed(1)}%">${STAR.repeat(5)}</span></span>`;
}
function gmbAsOf() { try { return new Intl.DateTimeFormat(lang === "de" ? "de-DE" : "en-GB", { dateStyle:"long" }).format(new Date(GMB.asof)); } catch (e) { return GMB.asof; } }
function gmbBadge() {
  const g = GMB.moabit;
  return `<a class="gmb" href="${gmbUrl(g)}" target="_blank" rel="noopener" title="${esc(t("gmb_title", { d:gmbAsOf() }))}"><b class="gmb-r">${num1(g.r)}</b><span class="gmb-m">${stars(g.r)}<small>${esc(t("gmb_n", { n:g.n, s:g.s }))}</small></span><span class="gmb-g">Google</span></a>`;
}
function gmbShop(key) {
  const g = GMB[key]; if (!g) return "";
  return `<a class="srate" href="${gmbUrl(g)}" target="_blank" rel="noopener" title="${esc(t("gmb_title", { d:gmbAsOf() }))}">${stars(g.r)}<b>${num1(g.r)}</b><span>${esc(t("gmb_shop", { n:g.n }))}</span></a>`;
}
