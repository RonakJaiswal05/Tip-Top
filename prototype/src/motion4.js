/* ===== Motion: reveals, stickers, drawers, count-up, slider sweep, tile tilt, nav ===== */
function setupLab() {}
const io = ANIM && "IntersectionObserver" in window ? new IntersectionObserver(ents => {
  ents.forEach(en => {
    if (!en.isIntersecting) return;
    const el = en.target; io.unobserve(el);
    if (el.classList.contains("wait")) { el.classList.remove("wait"); el.classList.add("on"); }
    else el.classList.add("in");
    el.querySelectorAll(":scope > .wipe").forEach(w => w.classList.add("in"));
    if (el.dataset.count) countUp(el);
    if (el.id === "cmp") sweep();
  });
}, { threshold:.2, rootMargin:"0px 0px -6% 0px" }) : null;
function watch(root = document) {
  if (!root) return;
  root.querySelectorAll(".wipe:not(.seen)").forEach(w => {
    w.classList.add("seen"); const host = w.parentElement;
    if (io) io.observe(host); else w.classList.add("in");
  });
  root.querySelectorAll("[data-rv]:not(.seen), .stk.wait:not(.seen), .drw.wait:not(.seen), [data-count]:not(.seen), #cmp:not(.seen)").forEach(el => {
    el.classList.add("seen");
    if (io) io.observe(el); else { el.classList.remove("wait"); el.classList.add("in", "on"); }
  });
}
function countUp(el) {
  const to = +el.dataset.count, nf = new Intl.NumberFormat(lang === "de" ? "de-DE" : "en-IE"), t0 = performance.now(), dur = 1600;
  const step = now => { const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 3); el.textContent = nf.format(Math.round(to * e / 10) * 10); if (k < 1) requestAnimationFrame(step); };
  requestAnimationFrame(step);
}
let swept = false;
function sweep() {
  if (swept || !ANIM) return; swept = true;
  const cmp = $("cmp"), pts = [[0, 50], [750, 80], [1650, 18], [2400, 50]];
  const ease = x => x < .5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2;
  let t0 = null;
  const frame = ts => {
    if (cmp.dataset.touched) return;
    if (t0 == null) t0 = ts;
    const e = ts - t0, i = pts.findIndex(p => p[0] > e);
    if (i === -1) { cmpSet(50); return; }
    const [a0, v0] = pts[i - 1], [a1, v1] = pts[i];
    cmpSet(v0 + (v1 - v0) * ease((e - a0) / (a1 - a0)));
    requestAnimationFrame(frame);
  };
  setTimeout(() => requestAnimationFrame(frame), 350);
}
function tilt(box) {
  if (!ANIM || !matchMedia("(pointer:fine)").matches) return;
  box.addEventListener("pointermove", e => {
    const d = e.target.closest(".dev"); if (!d || !box.contains(d)) return;
    const r = d.querySelector(".tile").getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)), y = Math.max(0, Math.min(1, (e.clientY - r.top) / r.height));
    d.classList.add("tilting");
    d.style.setProperty("--ry", ((x - .5) * 16).toFixed(2) + "deg");
    d.style.setProperty("--rx", ((.5 - y) * 16).toFixed(2) + "deg");
    d.style.setProperty("--gx", (x * 100).toFixed(1) + "%");
    d.style.setProperty("--gy", (y * 100).toFixed(1) + "%");
  });
  box.addEventListener("pointerout", e => {
    const d = e.target.closest(".dev"); if (!d || d.contains(e.relatedTarget)) return;
    d.classList.remove("tilting"); d.style.setProperty("--rx", "0deg"); d.style.setProperty("--ry", "0deg");
  });
}
tilt($("heroDevs")); tilt($("bldBody"));
(function () {
  const nav = document.querySelector(".nav"); let last = scrollY, tick = false;
  const upd = () => {
    const y = scrollY, h = document.documentElement.scrollHeight - innerHeight;
    nav.classList.toggle("scrolled", y > 8);
    if (ANIM && !document.documentElement.classList.contains("menu-open")) { if (y > last + 4 && y > 320) nav.classList.add("hide"); else if (y < last - 4 || y < 320) nav.classList.remove("hide"); }
    nav.style.setProperty("--p", h > 0 ? (y / h).toFixed(4) : 0);
    last = y; tick = false;
  };
  addEventListener("scroll", () => { if (!tick) { tick = true; requestAnimationFrame(upd); } }, { passive:true });
  nav.addEventListener("focusin", () => nav.classList.remove("hide"));
  upd();
})();
addEventListener("keydown", e => { if (e.key === "Escape" && !$("bld").hidden && $("drawer").hidden) closeBuilder(); });
(function () {
  const btn = $("menuBtn"), pnl = $("mnav"); if (!btn || !pnl) return;
  $("mnavCall").innerHTML = ic("call") + "<span>030 814 757 91</span>";
  const set = o => {
    btn.setAttribute("aria-expanded", o); pnl.hidden = !o;
    document.documentElement.classList.toggle("menu-open", o);
    if (o) document.querySelector(".nav").classList.remove("hide");
  };
  btn.addEventListener("click", () => set(btn.getAttribute("aria-expanded") !== "true"));
  pnl.addEventListener("click", e => { if (e.target.closest("a")) set(false); });
  addEventListener("keydown", e => { if (e.key === "Escape" && !pnl.hidden) { set(false); btn.focus(); } });
  matchMedia("(min-width:901px)").addEventListener("change", e => { if (e.matches) set(false); });
})();
