/* Signature pad for the purchase contract (A7): finger or pen on the tablet. */
(function () {
  const c = document.getElementById("sigPad"); if (!c) return;
  const ctx = c.getContext("2d"); let drawing = false, drawn = false, last = null;
  ctx.lineWidth = 3; ctx.lineCap = "round"; ctx.lineJoin = "round"; ctx.strokeStyle = "#12141C";
  ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, c.width, c.height);
  const pos = e => { const r = c.getBoundingClientRect(); return [(e.clientX - r.left) * c.width / r.width, (e.clientY - r.top) * c.height / r.height]; };
  c.addEventListener("pointerdown", e => { drawing = true; last = pos(e); c.setPointerCapture(e.pointerId); e.preventDefault(); });
  c.addEventListener("pointermove", e => { if (!drawing) return; const p = pos(e); ctx.beginPath(); ctx.moveTo(last[0], last[1]); ctx.lineTo(p[0], p[1]); ctx.stroke(); last = p; drawn = true; e.preventDefault(); });
  c.addEventListener("pointerup", () => { drawing = false; });
  document.getElementById("sigClear").addEventListener("click", () => { ctx.fillRect(0, 0, c.width, c.height); drawn = false; });
  document.getElementById("signForm").addEventListener("submit", () => { document.getElementById("sigData").value = drawn ? c.toDataURL("image/png") : ""; });
})();
