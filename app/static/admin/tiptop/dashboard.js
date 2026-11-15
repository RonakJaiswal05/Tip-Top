/* Dashboard: reload when a new request arrives (checked every 5 seconds) and notify the browser (A6). */
(function () {
  let last = null;
  async function poll() {
    try {
      const r = await fetch("/admin/dashboard/poll/", { credentials: "same-origin" }); if (!r.ok) return;
      const j = await r.json();
      if (last !== null && j.latest > last) {
        if ("Notification" in window && Notification.permission === "granted") new Notification("TipTop: neue Anfrage", { body: j.text || "" });
        location.reload();
      }
      last = j.latest;
    } catch (e) {}
  }
  document.addEventListener("click", () => { if ("Notification" in window && Notification.permission === "default") Notification.requestPermission(); }, { once: true });
  poll(); setInterval(poll, 5000);
})();
