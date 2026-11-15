/* Request inbox: checks every 5 seconds for new requests and shows a browser notification (A6). */
(function () {
  if (!document.body.classList.contains("change-list")) return;
  const url = "/admin/leads/request/poll/";
  let last = null, asked = false;
  const banner = document.createElement("div");
  banner.className = "messagelist"; banner.hidden = true;
  banner.innerHTML = '<li class="info"><a href="">Neue Anfrage eingegangen – Liste aktualisieren</a></li>';
  const anchor = document.getElementById("content"); if (anchor) anchor.prepend(banner);
  async function poll() {
    try {
      const r = await fetch(url, { credentials: "same-origin" }); if (!r.ok) return;
      const j = await r.json();
      if (last !== null && j.latest > last) {
        banner.hidden = false;
        if ("Notification" in window && Notification.permission === "granted") new Notification("TipTop: neue Anfrage", { body: j.text || "" });
      }
      last = j.latest;
    } catch (e) {}
  }
  document.addEventListener("click", () => { if (!asked && "Notification" in window && Notification.permission === "default") { asked = true; Notification.requestPermission(); } }, { once: true });
  poll(); setInterval(poll, 5000);
})();
