# Client voice note 17 Nov 2026 (evening): phone repair photos showed for tablets, laptops and consoles, and the
# header logo was cut out of the shop sign photo. Phone photos now only show for phones; other device types get
# their own photos once img/<id>.jpg exists (IMG_HAVE is written here from the img folder), otherwise a tile in the
# device colour. Logo files are the clean vector redraw in img/logo-tiptop.svg and img/logo-mark.svg.
import os as _os
_REP_CAT = {
  "tablet": [("display","tab-display"),("battery","tab-battery"),("port","tab-port"),("back","tab-back"),("camera","tab-camera"),("water","tab-water")],
  "laptop": [("display","lap-display"),("battery","lap-battery"),("keyboard","lap-keyboard"),("port","lap-port"),("fan","lap-fan"),("water","lap-water")],
  "console": [("hdmi","con-hdmi"),("fan","con-fan"),("drift","con-drift"),("tmr","con-drift"),("display","con-display"),("drive","con-drive"),("psu","con-psu")],
}
_imgdir = 'img/' if _os.path.isdir('img') else '../img/'  # local build runs next to img/, the portable src/ build one level down
_have = sorted({i for v in _REP_CAT.values() for _, i in v if _os.path.exists(_imgdir + i + '.jpg')})
_js_cat = "{ " + ", ".join(c + ":{" + ",".join(f'{k}:"{i}"' for k, i in v) + "}" for c, v in _REP_CAT.items()) + " }"
rep('''const REP_IMG = { display:"rep-display", battery:"rep-battery", port:"rep-port", back:"rep-back", camera:"rep-camera", water:"rep-water", cport:"rep-port" };''',
    '''const REP_IMG = { display:"rep-display", battery:"rep-battery", port:"rep-port", back:"rep-back", camera:"rep-camera", water:"rep-water", cport:"rep-port" };
// Phone repair photos are for phones only. Tablets, laptops and consoles use their own photos (REP_CAT) as soon as
// the file exists in img/ (IMG_HAVE is filled in by the build), otherwise a tile in the device colour.
const REP_CAT = ''' + _js_cat + ''';
const IMG_HAVE = new Set(''' + repr(_have).replace("'", '"') + ''');
function repImg(cat, k) {
  if (!cat || cat === "phone") return REP_IMG[k] || null;
  const id = REP_CAT[cat] && REP_CAT[cat][k];
  return id && IMG_HAVE.has(id) ? id : null;
}''')
rep('''<span class="rc-m">${REP_IMG[k] ? ph(REP_IMG[k]) : `<span class="icon-tile">''',
    '''<span class="rc-m">${repImg(m.cat, k) ? ph(repImg(m.cat, k)) : `<span class="icon-tile">''')
rep('''    <div class="rgrid">${top.map(card).join("")}</div>${restHtml}''',
    '''    <div class="rgrid" style="--tc:var(--t-${m.cat});--cc:var(--c-${m.cat})">${top.map(card).join("")}</div>${restHtml}''')
rep('''function sideImgId() {
  if (B.hoverKey && REP_IMG[B.hoverKey]) return REP_IMG[B.hoverKey];
  const k = B.sel.map(s => s.key).reverse().find(x => REP_IMG[x]);
  if (k) return REP_IMG[k];''',
    '''function sideImgId() {
  const ri = k => repImg(B.cat, k);
  if (B.hoverKey && ri(B.hoverKey)) return ri(B.hoverKey);
  const k = B.sel.map(s => s.key).reverse().find(x => ri(x));
  if (k) return ri(k);''')

# Image list: prompts for the 18 new device photos, appended so the existing numbers (and "attach 06 ..." notes) stay valid.
_SHOT_PS = " Same set-up as the phone repair photos: blue anti-static mat, macro lens, bright daylight. Logos and button symbols not readable. Portrait 2:3."
_SHOT_NOTE = " Same set-up as the phone repair photos: blue anti-static mat, macro lens, bright daylight. The device is generic: no logo, no brand name, not resembling any real product. Portrait 2:3."
_NEW = [
  ("tab-display","Tablet: display","rep-display","A tablet with a badly shattered screen lying on the mat next to a new replacement tablet screen in its clear protective film with a coloured pull tab, a pink opening pick and a blue suction cup. It must clearly read as a tablet: large, thin, rounded corners, slim bezels."),
  ("tab-battery","Tablet: battery","rep-battery","An opened tablet on the mat with its screen lifted away, gloved fingers (blue nitrile) lifting one of its two large flat battery cells out by the adhesive pull tabs, a new battery beside it."),
  ("tab-port","Tablet: charging port","rep-port","Close-up of the bottom edge of a tablet on the mat, a gloved hand cleaning the USB-C port with a small anti-static brush with an orange handle. The tablet's large flat body fills the background."),
  ("tab-back","Tablet: housing","rep-back","A tablet face down on the mat with a dented, bent aluminium back near one corner and a single camera bump, a yellow opening pick and a small heat pad beside it."),
  ("tab-camera","Tablet: camera","rep-camera","A small tablet rear camera module held in fine tweezers above the opened tablet on the mat, the lens cover glass cracked."),
  ("tab-water","Tablet: water damage","rep-water","A wet tablet opened on the mat, water droplets on the frame, its logic board in a small ultrasonic cleaner basket beside it, a plain unlabeled bottle of isopropyl alcohol and a soft brush."),
  ("lap-display","Laptop: display","rep-display","An open silver laptop on the mat with a cracked screen showing black ink bleed, a new replacement laptop panel leaning beside it, a small screwdriver and a pink opening pick."),
  ("lap-battery","Laptop: battery","rep-battery","A laptop upside down on the mat with its bottom cover removed, gloved hands lifting out the flat battery pack, a new battery beside it, tiny screws in a magnetic tray."),
  ("lap-keyboard","Laptop: keyboard","rep-port","Close-up of a laptop keyboard on the mat, a few keycaps removed and lying beside it, a gloved hand fitting a keycap with tweezers. Keys without readable lettering."),
  ("lap-port","Laptop: charging port","rep-port","Close-up of the side of a laptop on the mat, a gloved hand cleaning its USB-C charging port with a small anti-static brush with an orange handle."),
  ("lap-fan","Laptop: fan and cleaning","rep-water","A laptop with the bottom cover removed on the mat, showing the cooling fan and copper heat pipe, a gloved hand brushing thick grey dust out of the fan, a small tube of thermal paste beside it."),
  ("lap-water","Laptop: water damage","rep-water","A laptop opened on the mat with coffee spilled on the keyboard, the bottom cover off and the logic board lifted out next to a small ultrasonic cleaner basket, a plain unlabeled bottle of isopropyl alcohol and a soft brush."),
  ("con-hdmi","Console: HDMI port","rep-port","Close-up of the back of a white PlayStation 5 Pro on the mat, the old HDMI port desoldered, a new HDMI port held in fine tweezers, the tip of a soldering iron at the edge of the frame."),
  ("con-fan","Console: fan and cleaning","rep-water","A PlayStation 5 Pro with its white side panels taken off on the mat, showing the large round cooling fan, a gloved hand brushing dust out of the fan, a soft brush and a small tube of thermal paste beside it."),
  ("con-drift","Console: controller sticks","rep-camera","A white PlayStation 5 DualSense controller opened on the mat, a gloved hand lifting out one analog joystick module with tweezers, a new TMR joystick module beside it."),
  ("con-display","Console: handheld display","rep-display","A handheld games console with a cracked screen on the mat, a new replacement screen beside it in clear protective film, a pink opening pick."),
  ("con-drive","Console: disc drive","rep-back","A white PlayStation 5 Pro on the mat with its detachable disc drive unit taken off and opened beside it, a gloved hand holding a small screwdriver."),
  ("con-psu","Console: power supply","rep-back","A PlayStation 5 Pro opened on the mat with its internal power supply board lifted out beside it, the red and black probes of a multimeter touching the board."),
]
_items = ",\n".join(f'''  {{ id:"{i}", short:"{n.split(': ')[1].capitalize()}", name:"{n}", ratio:"2:3", px:"1024×1536", where:"Repair cards ({n.split(':')[0].lower()})", attach:"img/{a}.jpg (style reference)",
    p:"{p}{_SHOT_NOTE if not ('PlayStation' in p) else _SHOT_PS}" + SHOT }}''' for i, n, a, p in _NEW)
rep('''p:"Night photo of the Beusselstraße 18 shop front from the owner, retouched by his brother in ChatGPT. Swap for a more realistic retouch if the client prefers." }
];''', '''p:"Night photo of the Beusselstraße 18 shop front from the owner, retouched by his brother in ChatGPT. Swap for a more realistic retouch if the client prefers." },
''' + _items + '''
];''')
s = s.replace('</style>', '''.rc .icon-tile{background:var(--tc,var(--fog));color:var(--cc,var(--ink))}
.logo .logo-full{border-radius:0}
</style>''', 1)

# Admin: adding a model that already exists is refused (it would create a second entry with the same id).
rep('/* ===== Language, routing, boot ===== */', '''Object.assign(T.en, { ad_dup:"{m} is already in the list. Change its prices under Prices." });
Object.assign(T.de, { ad_dup:"{m} ist schon in der Liste. Preise ändern Sie unter Preise." });
/* ===== Language, routing, boot ===== */''')

# Big repair cards for consoles: handheld screen first, then sticks, battery and port; home consoles keep HDMI, fan, drive, power supply.
rep('console:["hdmi","fan","drift","tmr","display","drive","psu","cport","battery","buttons"] };',
    'console:["display","hdmi","drift","tmr","battery","cport","fan","drive","psu","buttons"] };')
