# 27 Nov 2026: changes Claude Code made directly in prototype/index.html at Ronak's request (see CLAUDE.md,
# "Requests for the chat"), carried into the sources so later builds keep them.
# 1. Logo: the client's original gold logo (cut-out by Claude Code), header and footer.
rep('<img class="logo-full" src="img/logo-tiptop.svg" alt="" width="201" height="46">', '<img class="logo-full" src="img/logo-tiptop.webp" alt="" width="145" height="46">')
rep('<img class="flogo" src="img/logo-tiptop.svg" alt="TipTop" width="245" height="56" loading="lazy">', '<img class="flogo" src="img/logo-tiptop.webp" alt="TipTop" width="202" height="64" loading="lazy">')
# 2. Footer: no "Admin" and no "Image prompts" links.
rep('''          <li><a href="#admin">Admin</a></li>
          <li><button type="button" id="imgLink" style="color:inherit;font:inherit;padding:0" data-t="img_btn"></button></li>
''', '')
rep('$("imgLink").addEventListener("click", () => { $("drawer").hidden = false; });',
    'if ($("imgLink")) $("imgLink").addEventListener("click", () => { $("drawer").hidden = false; });')
# 3. Demo admin: one fixed demo login (js/admin.js) and its texts.
rep('ad_demo:"Demo sign-in: any username and password work. The real admin runs on Django with secure logins.",',
    'ad_demo:"Demo admin: changes here are only saved in this browser and don\'t reach the shop.", ad_wrong:"Wrong username or password.",')
rep('ad_demo:"Demo-Anmeldung: Jeder Name und jedes Passwort funktioniert. Der echte Admin läuft auf Django mit sicherem Login.",',
    'ad_demo:"Demo-Admin: Änderungen hier werden nur in diesem Browser gespeichert und gehen nicht an den Laden.", ad_wrong:"Benutzername oder Passwort stimmt nicht.",')
# 4. Desktop hero (where the film plays) opens on the film's first frame instead of the repair photo.
rep('''    im.onerror = () => { IMG_STATE[id] = false; im.remove(); };
    if (!(IMG[id] && IMG[id].real))''', '''    im.onerror = () => { IMG_STATE[id] = false; im.remove(); };
    // 27 Nov (Ronak): where the hero film plays, the hero opens on the film's first frame, not the repair photo
    const filmMq = id === "hero" && f.closest("#heroMedia") ? matchMedia("(min-width:901px) and (hover:hover) and (pointer:fine) and (prefers-reduced-motion:no-preference)") : null;
    if (filmMq && filmMq.matches) { im.src = (window.__IMGDATA && window.__IMGDATA["hero-film"]) || "img/hero-film.jpg?v=2"; f.appendChild(im); return; }
    if (!(IMG[id] && IMG[id].real))''')
# 5. Before/after never crops the phone; on wide screens the 3:2 box gets narrower instead of shorter.
s = s.replace('</style>', '''/* 27 Nov (Ronak): before/after never crops the phone; on wide screens the 3:2 box gets narrower instead of shorter */
.cmp{max-height:none;max-width:calc(80vh * 1.5);margin-left:auto;margin-right:auto}
</style>''', 1)
