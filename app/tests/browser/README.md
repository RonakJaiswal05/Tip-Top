# Browser checks

Run against a local server (`manage.py runserver`), in the browser console or a test runner.

1. `python tests/browser/expected_labels.py` writes `static/test/expected_labels.json` (the server's price labels
   for every model and repair, in German and English).
2. Paste `price_check.js` into the console on `/de/` (or `/en/` with `LANG = "en"`). It opens the calculator for
   each of the 180 models through the deep link, expands all repairs and compares every label. Expect
   `mismatches: 0`.
3. Accessibility: `npm install axe-core`, copy `axe.min.js` to `static/test/`, then in the console:
   `const s=document.createElement('script');s.src='/static/test/axe.min.js';document.head.append(s);`
   and `(await axe.run()).violations`.

`static/test/` is git-ignored and must not be deployed.
