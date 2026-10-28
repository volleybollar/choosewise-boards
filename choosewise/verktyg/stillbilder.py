"""Kontroll av en board: stillbilder vid givna tider + koll av kamerazonen.

Kör (med en lokal server igång i repot: python3 -m http.server 8765):
  /opt/homebrew/bin/python3.12 -I choosewise/verktyg/stillbilder.py \
      http://127.0.0.1:8765/choosewise/boards/D44-linje.html  /tmp/d44  2,6,10

Skriver /tmp/d44-2.0.png osv. och för varje tid "ok" eller "krock" med de
element som går in i kamerazonen (x >= 1570 och y >= 720). "fel" listar
JavaScript-fel på sidan; den ska vara tom.
"""
import sys
from playwright.sync_api import sync_playwright

url, ut, tider = sys.argv[1], sys.argv[2], [float(t) for t in sys.argv[3].split(',')]

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1920, 'height': 1080})
    fel = []
    pg.on('pageerror', lambda e: fel.append(str(e)))
    pg.goto(url)
    pg.wait_for_timeout(800)
    pg.evaluate("document.querySelector('button') && document.querySelector('button').remove()")
    print('längd', pg.evaluate("tavla.tl.duration()"), 'ljud', pg.evaluate("JSON.stringify(tavla.ljud)"))
    for t in tider:
        # "void": annars försöker Playwright skicka tillbaka hela tidslinjen och hänger.
        pg.evaluate(f"void tavla.tl.pause({t}, false)")
        pg.wait_for_timeout(150)
        krock = pg.evaluate("""() => [...document.querySelectorAll('.cw *:not(.kamerazon)')].filter(e => {
            const r = e.getBoundingClientRect(), s = getComputedStyle(e);
            if (!r.width || !r.height || +s.opacity === 0 || s.visibility === 'hidden' || e.children.length) return false;
            return r.right > 1570 && r.bottom > 720 && r.left < 1920 && r.top < 1080;
          }).map(e => e.className + ':' + (e.textContent || '').slice(0, 20))""")
        pg.screenshot(path=f"{ut}-{t}.png")
        print(t, 'krock' if krock else 'ok', krock)
    print('fel', fel)
    b.close()
