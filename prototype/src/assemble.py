# Splices the original JS blocks into src4.html and writes ../index.html (run build4.py first).
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, 'src4.html'), encoding='utf-8').read()
for k, f in [('ENGINE', 'engine.js'), ('PARSE', 'parse.js'), ('VOICE', 'voice.js'), ('OPEN', 'open.js'), ('ADMIN', 'admin.js')]:
    assert '/*%s*/' % k in s, k
    s = s.replace('/*%s*/' % k, open(os.path.join(HERE, 'js', f), encoding='utf-8').read())
open(os.path.join(HERE, '..', 'index.html'), 'w', encoding='utf-8').write(s)
open(os.path.join(HERE, '_check.js'), 'w', encoding='utf-8').write(re.search(r'<script>(.*)</script>', s, re.S).group(1))
print('assembled', len(s), '-> ../index.html  (syntax check: node --check _check.js)')
