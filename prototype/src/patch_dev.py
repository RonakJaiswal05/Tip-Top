# ---- device optimisation: viewport, mobile menu, responsive lazy images ----
rep('<meta name="viewport" content="width=device-width, initial-scale=1">', '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="theme-color" content="#ffffff">')
rep('<button type="button" class="cta" data-open-builder><span data-t="cta"></span></button>\n  <span class="prog" aria-hidden="true"></span>\n</header>',
    open('menu4.html', encoding='utf-8').read())
i0 = s.index('const IMG_STATE = {};'); i1 = s.index('/*ENGINE*/')
s = s[:i0] + open('hydrate4.js', encoding='utf-8').read() + '\n' + s[i1:]
