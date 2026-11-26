/* ===== Legal pages: shared bits ===== */
// Legal pages live on hash routes so they work inside the prototype and the standalone file.
// Live site: these become Django CMS pages (/impressum, /datenschutz, ...) editable in the admin.
const LEGAL_KEYS = ["impressum", "datenschutz", "agb", "widerruf", "cookies", "barrierefreiheit"];
const LEGAL_UPD = { de:"26. November 2026", en:"26 November 2026" };
// Shop email confirmed in the call of 25 Nov 2026 (no access to the old info@ address).
const LG_MAIL = '<a href="mailto:tiptophandyreparatur@gmail.com">tiptophandyreparatur@gmail.com</a>';
const LG_TEL = '<a href="tel:+493081475791">030 814 757 91</a>';
// Sole trader (Einzelunternehmer), no GmbH. Owner confirmed in the call of 25 Nov 2026: Mostafa Khodr (K-H-O-D-R).
const LG_FIRM = "TipTop Service 24 Handy Reparatur Berlin";
const fillIn = s => `<mark class="fill">${s}</mark>`;
const LG_OWNER = "Mostafa Khodr";
const extL = (u, x) => `<a href="${u}" target="_blank" rel="noopener">${x || u.replace(/^https?:\/\/(www\.)?/, "")}</a>`;
const intL = (h, x) => `<a href="#${h}">${x}</a>`;
const abs = items => `<ol class="lg-abs">${items.map(x => `<li>${x}</li>`).join("")}</ol>`;
const ulist = items => `<ul>${items.map(x => `<li>${x}</li>`).join("")}</ul>`;

/* Everything the site stores on a visitor's device. Used by the cookie settings and the cookie policy table. */
const COOKIES = {
  de: {
    necessary: [
      ["tt-consent", "TipTop (lokaler Speicher)", "Speichert deine Cookie-Auswahl, die Version dieses Hinweises, den Zeitpunkt und eine zufällige Kennung als Nachweis.", "12 Monate"],
      ["tt-lang", "TipTop (lokaler Speicher)", "Merkt sich, ob du die Seite auf Deutsch oder Englisch sehen möchtest.", "bis du ihn löschst"],
      ["tt-mic-ok", "TipTop (lokaler Speicher)", "Merkt sich, dass du den Hinweis zur Spracheingabe bestätigt hast.", "bis du ihn löschst"],
      ["csrftoken", "TipTop (Cookie, Live-System)", "Schützt Formulare davor, von fremden Seiten abgeschickt zu werden.", "1 Jahr"],
      ["sessionid", "TipTop (Cookie, Live-System)", "Hält Mitarbeitende im Admin-Bereich angemeldet. Wird für Besucher nicht gesetzt.", "2 Wochen"],
      ["tt-reqs, tt-ovr, tt-added", "TipTop (lokaler Speicher, nur Prototyp)", "Simuliert im Design-Prototyp die Daten des Admin-Bereichs in deinem Browser. Entfällt im Live-System.", "bis du ihn löschst"]
    ],
    stats: [
      ["_pk_id.*", "Matomo, eigener Server in Deutschland", "Unterscheidet Besuche, ohne dich zu identifizieren. IP-Adresse wird gekürzt.", "13 Monate"],
      ["_pk_ses.*", "Matomo, eigener Server in Deutschland", "Fasst Seitenaufrufe eines Besuchs zusammen.", "30 Minuten"]
    ],
    marketing: [
      ["_gcl_au", "Google Ireland Limited", "Misst, ob eine Google-Anzeige zu einer Anfrage geführt hat.", "90 Tage"],
      ["_fbp", "Meta Platforms Ireland Limited", "Misst den Erfolg von Anzeigen auf Facebook und Instagram.", "90 Tage"]
    ]
  },
  en: {
    necessary: [
      ["tt-consent", "TipTop (local storage)", "Stores your cookie choice, the version of this notice, the time and a random ID as proof.", "12 months"],
      ["tt-lang", "TipTop (local storage)", "Remembers whether you want the site in German or English.", "until you delete it"],
      ["tt-mic-ok", "TipTop (local storage)", "Remembers that you confirmed the voice input notice.", "until you delete it"],
      ["csrftoken", "TipTop (cookie, live site)", "Stops forms being submitted from other websites.", "1 year"],
      ["sessionid", "TipTop (cookie, live site)", "Keeps staff signed in to the admin area. Never set for visitors.", "2 weeks"],
      ["tt-reqs, tt-ovr, tt-added", "TipTop (local storage, prototype only)", "Simulates the admin data in your browser for this design prototype. Not used on the live site.", "until you delete it"]
    ],
    stats: [
      ["_pk_id.*", "Matomo, our own server in Germany", "Tells visits apart without identifying you. IP addresses are shortened.", "13 months"],
      ["_pk_ses.*", "Matomo, our own server in Germany", "Groups the pages viewed during one visit.", "30 minutes"]
    ],
    marketing: [
      ["_gcl_au", "Google Ireland Limited", "Measures whether a Google ad led to a request.", "90 days"],
      ["_fbp", "Meta Platforms Ireland Limited", "Measures how ads on Facebook and Instagram perform.", "90 days"]
    ]
  }
};
const ckTable = (lang, cat) => {
  const h = lang === "de" ? ["Name", "Anbieter", "Zweck", "Dauer"] : ["Name", "Provider", "Purpose", "Duration"];
  return `<div class="lg-tw"><table class="lg-tbl"><thead><tr>${h.map(x => `<th scope="col">${x}</th>`).join("")}</tr></thead><tbody>${COOKIES[lang][cat].map(r => `<tr><td><code>${r[0]}</code></td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join("")}</tbody></table></div>`;
};
