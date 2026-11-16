"""Ramkoll: prövar varje bildruta i en board efter fel som tittaren ser direkt.

Spolar boardens tidslinje (tavla.tl) i steg om 0,1 s och mäter den riktiga
texten i varje läge:
  - text utanför bilden (eller marginalen) eller inne i Borumi-rutan
  - text som sticker ut ur rutan, kortet eller etiketten den står på
  - två texter som ligger på varandra
Text som är på väg in eller ut över kanten får passera; den ska vara på plats
när den har landat. Ett avsiktligt lager (ett spökord bakom en rad) märks med
data-layered, en remsa som ska löpa ut över kanten med data-bleed.

Kör (med en lokal server igång i repot: python3 -m http.server 8765):
  /opt/homebrew/bin/python3.12 -I choosewise/verktyg/ramkoll.py \\
      http://127.0.0.1:8765/choosewise/boards/D44-linje.html [fler adresser] [--steg 0.1] [--marginal 24]

Skriver "ren" eller en lista "t=1.2-1.8s  vad" per board. Avslutar med kod 1
om någon board har fel.

Mätningen är porterad från frame-audit.mjs i motion-director
(github.com/sharbelxyz/motion-director), MIT-licens:
  Copyright (c) 2026 Sharbel
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions: The above copyright
  notice and this permission notice shall be included in all copies or
  substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS",
  WITHOUT WARRANTY OF ANY KIND.
"""
import sys
from playwright.sync_api import sync_playwright

argv = sys.argv[1:]
def val(namn, standard):
    return float(argv[argv.index(namn) + 1]) if namn in argv else standard
STEG, MARGINAL = val('--steg', 0.1), val('--marginal', 24)
adresser = [a for i, a in enumerate(argv) if a.startswith('http') and (i == 0 or not argv[i - 1].startswith('--'))]

# Mätningen körs inne i sidan i varje läge. Borumi-rutan: x >= 1570 och y >= 720.
PROBE = """(() => {
  const W = 1920, H = 1080, M = __M__, KX = 1570, KY = 720;
  const vis = (el) => { let o = 1; for (let e = el; e && e.nodeType === 1; e = e.parentElement) { const cs = getComputedStyle(e); if (cs.display === "none" || cs.visibility === "hidden") return 0; o *= +cs.opacity; } return o; };
  const name = (el) => (el.id ? "#" + el.id : (el.className && typeof el.className === "string" ? "." + el.className.trim().split(/\\s+/)[0] : el.tagName.toLowerCase()));
  // en ruta som syns: bakgrundsfärg eller bakgrundsbild
  const paints = (e) => { const cs = getComputedStyle(e); if (cs.backgroundClip === "text" || cs.webkitBackgroundClip === "text") return false; return (cs.backgroundColor && !/rgba\\(0, 0, 0, 0\\)|transparent/.test(cs.backgroundColor)) || (cs.backgroundImage && cs.backgroundImage !== "none"); };
  // den del av en textrad som syns genom fönster med overflow: hidden (en rulle, ett mätarverk)
  // eller genom en mask clip-path: inset(...) (ett ord som avslöjas från vänster).
  // Syns mindre än 40 % av raden räknas den som dold.
  const clip = (el, q) => {
    let c = { left: q.left, top: q.top, right: q.right, bottom: q.bottom };
    const snitt = (b) => { c = { left: Math.max(c.left, b.left), top: Math.max(c.top, b.top), right: Math.min(c.right, b.right), bottom: Math.min(c.bottom, b.bottom) }; };
    for (let e = el; e && e !== document.body; e = e.parentElement) {
      const cs = getComputedStyle(e), b = e.getBoundingClientRect();
      if (cs.overflow === "hidden" || cs.overflow === "clip") snitt(b);
      const m = /^inset\\(([^)]*)\\)/.exec(cs.clipPath);
      if (m) {
        // inset(topp höger botten vänster), i procent av rutan eller i px
        let v = m[1].split(/\\s+/).slice(0, 4); while (v.length < 4) v.push(v[v.length === 3 ? 1 : 0]);
        const mat = (s, sida) => s.endsWith("%") ? parseFloat(s) / 100 * sida : parseFloat(s) || 0;
        const w = b.right - b.left, h = b.bottom - b.top;
        snitt({ left: b.left + mat(v[3], w), top: b.top + mat(v[0], h), right: b.right - mat(v[1], w), bottom: b.bottom - mat(v[2], h) });
      }
    }
    const w = c.right - c.left, h = c.bottom - c.top;
    return w > 0.4 * (q.right - q.left) && h > 0.4 * (q.bottom - q.top) ? c : null;
  };
  // täckt: det som ligger överst mitt på raden är en ruta med bakgrund som inte hör till texten.
  // Bara rutor upp till den gemensamma föräldern räknas, så två etiketter på samma kort som
  // ligger på varandra fortfarande blir ett fel.
  const covered = (el, q) => {
    const x = (q.left + q.right) / 2, y = (q.top + q.bottom) / 2;
    if (x < 0 || y < 0 || x >= W || y >= H) return false;
    const hit = document.elementFromPoint(x, y);
    if (!hit || el.contains(hit) || hit.contains(el)) return false;
    for (let e = hit; e && !e.contains(el); e = e.parentElement) if (paints(e) && +getComputedStyle(e).opacity > 0.5) return true;
    return false;
  };
  const texts = [];
  const tw = document.createTreeWalker(document.querySelector(".cw"), NodeFilter.SHOW_TEXT);
  for (let n; (n = tw.nextNode());) {
    if (!n.textContent.trim()) continue;
    const el = n.parentElement; if (el.closest("svg, script, style, .kamerazon")) continue;
    if (vis(el) < 0.35) continue;
    const range = document.createRange(); range.selectNodeContents(n);
    const rs = [...range.getClientRects()].filter((r) => r.width > 2 && r.height > 2).map((q) => clip(el, q)).filter(Boolean);
    if (!rs.length) continue;
    const r = { left: Math.min(...rs.map((q) => q.left)), top: Math.min(...rs.map((q) => q.top)), right: Math.max(...rs.map((q) => q.right)), bottom: Math.max(...rs.map((q) => q.bottom)) };
    // text som väntar helt utanför bilden syns inte, och text bakom ett annat kort inte heller
    if (r.right <= 0 || r.left >= W || r.bottom <= 0 || r.top >= H) continue;
    if (rs.every((q) => covered(el, q))) continue;
    if (el.closest("[data-bleed]")) continue;
    // varje element får ett fast nummer, så att text som skrivs fram räknas som samma fel
    el.dataset.rk = el.dataset.rk || String(window.__rkNr = (window.__rkNr || 0) + 1);
    texts.push({ el, r, rs, txt: n.textContent.trim().slice(0, 28), layered: !!el.closest("[data-layered]") });
  }
  // Proven gäller text som har landat. Text som är på väg (in över kanten, en stämpel som slår
  // ner, ett kort som flyger förbi rubriken) får passera; den ska vara rätt när den står still.
  for (const t of texts) {
    const key = t.el.dataset.rk + "|" + t.txt, prev = (window.__rkPrev || {})[key], r = t.r;
    t.moving = !prev || (Math.abs(prev.left - r.left) > 6 || Math.abs(prev.top - r.top) > 6 || Math.abs((prev.right - prev.left) - (r.right - r.left)) > 6);
    (window.__rkNext = window.__rkNext || {})[key] = r;
  }
  const out = [];
  for (const t of texts) {
    const { r, moving } = t, who = name(t.el) + ' "' + t.txt + '"', nr = t.el.dataset.rk;
    if (moving) continue;
    // 1. inom bilden och utanför Borumi-rutan
    if ((r.left < M - 1 || r.top < M - 1 || r.right > W - M + 1 || r.bottom > H - M + 1)) out.push([nr + "|kant", who + " utanför bildens marginal (" + [r.left, r.top, r.right, r.bottom].map(Math.round).join(",") + ")"]);
    if (t.rs.some((q) => q.right > KX && q.bottom > KY)) out.push([nr + "|borumi", who + " i Borumi-rutan"]);
    // 2. inne i rutan den står på: närmaste förälder med bakgrund som är mindre än bilden
    for (let e = t.el; e && !e.classList.contains("cw"); e = e.parentElement) {
      if (!paints(e)) continue; const b = e.getBoundingClientRect(); if (b.width >= W * 0.98 && b.height >= H * 0.98) break;
      const cs = getComputedStyle(e), pl = Math.min(parseFloat(cs.paddingLeft) || 0, 40) * 0.4, pt = Math.min(parseFloat(cs.paddingTop) || 0, 40) * 0.25;
      if (r.left < b.left + pl - 1 || r.right > b.right - pl + 1 || r.top < b.top + pt - 2 || r.bottom > b.bottom - pt + 2) out.push([nr + "|ruta", who + " sticker ut ur " + name(e)]);
      break;
    }
  }
  // 3. text på text, från olika element
  for (let i = 0; i < texts.length; i++) for (let j = i + 1; j < texts.length; j++) {
    const a = texts[i], b = texts[j]; if (a.moving || b.moving || a.layered || b.layered) continue; if (a.el === b.el || a.el.contains(b.el) || b.el.contains(a.el)) continue;
    // orden i ett och samma textblock (en delad rubrik) räknas som ett
    const blk = (e) => e.closest("h1, h2, h3, h4, p, li, [data-block]") || e;
    if (blk(a.el) === blk(b.el)) continue;
    // jämför bläcket, inte radboxen: en radbox är ~20 % högre än bokstäverna i varje kant.
    // Rad för rad, så att spans som bryts över flera rader i samma stycke inte räknas som överlapp.
    const ink = (r) => { const h = (r.bottom - r.top) * 0.2; return { left: r.left, right: r.right, top: r.top + h, bottom: r.bottom - h }; };
    const krock = a.rs.some((qa) => b.rs.some((qb) => { const A = ink(qa), B = ink(qb);
      return Math.min(A.right, B.right) - Math.max(A.left, B.left) > 4 && Math.min(A.bottom, B.bottom) - Math.max(A.top, B.top) > 4; }));
    if (krock) out.push([a.el.dataset.rk + "|" + b.el.dataset.rk, name(a.el) + ' "' + a.txt + '" ligger på ' + name(b.el) + ' "' + b.txt + '"']);
  }
  window.__rkPrev = window.__rkNext || {}; window.__rkNext = {};
  return out;
})()""".replace('__M__', str(int(MARGINAL)))


def tider(ts):
    """Slår ihop tider i följd till intervall: 1.2-1.8s, 4.0s."""
    runs, a, b = [], ts[0], ts[0]
    for t in ts[1:]:
        if t - b <= STEG * 1.5:
            b = t
        else:
            runs.append((a, b)); a = b = t
    runs.append((a, b))
    return ', '.join(f'{x}s' if x == y else f'{x}-{y}s' for x, y in runs)


nagot_fel = False
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1920, 'height': 1080})
    for url in adresser:
        jsfel = []
        lyssnare = lambda e: jsfel.append(str(e))
        pg.on('pageerror', lyssnare)
        pg.goto(url)
        pg.evaluate("document.fonts.ready.then(() => 0)")
        pg.wait_for_timeout(400)
        pg.evaluate("document.querySelector('button') && document.querySelector('button').remove()")
        # förhandsvisningens Borumi-ram döljs, annars "täcker" den text som hamnat i rutan
        pg.evaluate("document.body.classList.add('dolj-kamera')")
        langd = pg.evaluate("tavla.tl.duration()")
        hittat = {}
        t = 0.0
        while t <= langd - 0.001:
            tt = round(t, 3)
            # "void": annars försöker Playwright skicka tillbaka hela tidslinjen och hänger.
            pg.evaluate(f"void tavla.tl.pause({tt}, false)")
            # samma element och samma slags fel blir en rad; texten från första gången visas
            for nyckel, fel in pg.evaluate(PROBE):
                hittat.setdefault(nyckel, [fel, []])[1].append(tt)
            t += STEG
        pg.remove_listener('pageerror', lyssnare)
        namn = url.rsplit('/', 1)[-1]
        if not hittat and not jsfel:
            print(f'{namn}: ren ({round(langd / STEG)} bildrutor)')
            continue
        nagot_fel = True
        print(f'{namn}: {len(hittat) + len(jsfel)} fel')
        for fel in jsfel:
            print(f'  JS-fel           {fel}')
        for fel, ts in sorted(hittat.values(), key=lambda x: x[1][0]):
            print(f'  {tider(ts):<16} {fel}')
    b.close()
sys.exit(1 if nagot_fel else 0)
