const IMG_STATE = {};
function imgSizes(f) {
  if (f.closest(".tile")) return "(max-width:599px) 44vw, (max-width:900px) 22vw, 200px";
  if (f.closest(".rep")) return "(max-width:520px) 76vw, (max-width:900px) 46vw, 440px";
  if (f.closest(".hero-frame")) return "(max-width:599px) 92vw, (max-width:900px) 40vw, 600px";
  if (f.closest(".lcard")) return "(max-width:599px) 84vw, (max-width:760px) 92vw, 700px";
  if (f.closest(".cmp")) return "(max-width:1400px) 96vw, 1400px";
  if (f.closest(".mini")) return "44px";
  if (f.closest(".rc")) return "160px";
  return "(max-width:700px) 92vw, 640px";
}
function hydrate(root = document) {
  root.querySelectorAll(".ph[data-img]:not(.tried)").forEach(f => {
    f.classList.add("tried");
    const id = f.dataset.img;
    if (IMG_STATE[id] === false) return;
    const im = document.createElement("img");
    im.alt = ""; im.decoding = "async";
    const eager = f.closest(".hero") || f.closest(".bld");
    if (eager) im.fetchPriority = f.closest(".hero-frame") ? "high" : "auto"; else im.loading = "lazy";
    im.onload = () => { IMG_STATE[id] = true; f.classList.add("loaded"); };
    im.onerror = () => { IMG_STATE[id] = false; im.remove(); };
    if (!(IMG[id] && IMG[id].real)) { im.sizes = imgSizes(f); im.srcset = `img/${id}-s.jpg 760w, img/${id}.jpg ${IMG[id] && IMG[id].ratio === "2:3" ? 1024 : IMG[id] && IMG[id].ratio === "1:1" ? 1254 : 1536}w`; }
    im.src = "img/" + id + ".jpg";
    f.appendChild(im);
  });
}
