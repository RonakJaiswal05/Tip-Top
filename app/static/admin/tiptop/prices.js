/* Price editor and price list: highlight changed fields (like the prototype's admin preview), warn before leaving
   unsaved, and in the price list send only the changed cells. */
(function () {
  document.querySelectorAll(".tt-ptable").forEach(t => {
    const form = t.closest("form"); if (!form) return;
    const grid = form.hasAttribute("data-grid"), info = form.querySelector(".tt-dirty");
    let dirty = false;
    const count = () => t.querySelectorAll("input.chg").length;
    t.addEventListener("input", e => {
      const i = e.target; if (i.type !== "number") return;
      i.classList.toggle("chg", i.value !== (i.dataset.def || "")); dirty = count() > 0;
      if (info) info.textContent = dirty ? count() + " geändert" : "";
    });
    form.addEventListener("submit", () => {
      dirty = false;
      if (grid) t.querySelectorAll("input[type=number]:not(.chg)").forEach(i => { i.disabled = true; });
    });
    addEventListener("beforeunload", e => { if (dirty) { e.preventDefault(); e.returnValue = ""; } });
  });
})();
