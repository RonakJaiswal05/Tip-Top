/* Price editor: highlight changed fields (like the prototype's admin preview) and warn before leaving unsaved. */
(function () {
  const t = document.querySelector(".tt-ptable"); if (!t) return;
  let dirty = false;
  t.addEventListener("input", e => {
    const i = e.target; if (i.type !== "number") return;
    i.classList.toggle("chg", i.value !== (i.dataset.def || "")); dirty = true;
  });
  t.closest("form").addEventListener("submit", () => { dirty = false; });
  addEventListener("beforeunload", e => { if (dirty) { e.preventDefault(); e.returnValue = ""; } });
})();
