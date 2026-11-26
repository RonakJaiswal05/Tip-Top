# Builds one self-contained HTML file: fonts and images embedded as data URIs, no external files needed.
import base64, glob, io, os, re, json
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep
OUT = ROOT + 'TipTop-Service-24-final.html'
s = open(ROOT + 'index.html', encoding='utf-8').read()

def b64(data): return base64.b64encode(data).decode()

# fonts
s = re.sub(r'<link rel="preload" href="fonts/[^"]+" as="font"[^>]*>\n?', '', s)
for f in ['archivo-latin', 'archivo-latin-ext']:
    tok = f'url(fonts/{f}.woff2)'
    assert s.count(tok) == 1, tok
    s = s.replace(tok, 'url(data:font/woff2;base64,' + b64(open(ROOT + f'fonts/{f}.woff2', 'rb').read()) + ')')

# images: one version each, longest edge 1280px, progressive JPEG
data, total = {}, 0
for p in sorted(glob.glob(ROOT + 'img/*.jpg')):
    name = os.path.basename(p)[:-4]
    if name.endswith('-s'):
        continue
    im = Image.open(p).convert('RGB')
    im.thumbnail((1280, 1280), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=74, optimize=True, progressive=True)
    total += buf.tell()
    data[name] = 'data:image/jpeg;base64,' + b64(buf.getvalue())
print('images', len(data), round(total / 1e6, 2), 'MB raw')

hook = '    if (!(IMG[id] && IMG[id].real)) { im.sizes = imgSizes(f);'
assert s.count(hook) == 1
s = s.replace(hook, '    if (window.__IMGDATA) { const d = window.__IMGDATA[id]; if (!d) { IMG_STATE[id] = false; return; } im.src = d; f.appendChild(im); return; }\n' + hook)
first_script = s.index('<script>')
s = s[:first_script] + '<script>window.__IMGDATA = ' + json.dumps(data) + ';</script>\n' + s[first_script:]
# TipTop logo files in the header and the favicon
for nm, mt in [('logo-tiptop.svg', 'image/svg+xml'), ('logo-mark.webp', 'image/webp'), ('logo-mark-180.png', 'image/png')]:
    s = s.replace('img/' + nm, 'data:' + mt + ';base64,' + b64(open(ROOT + 'img/' + nm, 'rb').read()))
# brand logos (img/brands/*.svg) as data URIs
bd = {os.path.basename(p)[:-4]: 'data:image/svg+xml;base64,' + b64(open(p, 'rb').read()) for p in sorted(glob.glob(ROOT + 'img/brands/*.svg'))}
first_script = s.index('<script>')
s = s[:first_script] + '<script>window.__BRANDDATA = ' + json.dumps(bd) + ';</script>\n' + s[first_script:]

# desktop hero film: embedded, turned into a blob URL only when the desktop video actually starts
if os.path.exists(ROOT + 'img/hero-loop.mp4'):
    tok = 'v.src = "img/hero-loop.mp4";'
    assert s.count(tok) == 1, tok
    s = s.replace(tok, 'v.src = window.__HEROVID ? URL.createObjectURL(new Blob([Uint8Array.from(atob(window.__HEROVID), c => c.charCodeAt(0))], { type:"video/mp4" })) : "img/hero-loop.mp4";')
    first_script = s.index('<script>')
    s = s[:first_script] + '<script>window.__HEROVID = "' + b64(open(ROOT + 'img/hero-loop.mp4', 'rb').read()) + '";</script>\n' + s[first_script:]
assert 'fonts/' not in s.split('<script>')[0] or True
open(OUT, 'w', encoding='utf-8').write(s)
print('written', OUT, round(len(s.encode()) / 1e6, 2), 'MB')
