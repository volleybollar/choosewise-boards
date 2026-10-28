"""Synk och export: boards som landar på Johans ord, som klipp för Borumi.

Kör (med en lokal server i repots rot: python3 -m http.server 8765):
  /opt/homebrew/bin/python3.12 -I choosewise/verktyg/synk.py choosewise/film-<namn>/plan.json

plan.json (tider i sekunder i den färdiga filmen):
  {
    "rost": "rost.wav",                       # valfri: Johans röst, bara för förhandsvisningen
    "fonster": [
      { "board": "D43-staplar.html",          # boardfil i samma mapp som plan.json
        "start": 12.4, "slut": 24.0,          # när boarden syns i filmen
        "ankare": [12.6, 14.1, 15.0] }        # när steg 1, 2, 3 … ska landa (ordens tider)
    ]
  }
  Ett ankare kan också peka ut ett visst steg: {"steg": 4, "tid": 14.1}.
  Stegen för en board listas med:  synk.py --steg <boardfil>

Hur tiden räknas: boardens steg hittas automatiskt ur GSAP-tidslinjen (tweens
som startar nära varandra är ett steg). Mellan två ankare spelas boarden i
normal fart till nästa steg och väntar sedan still tills ordet sägs. Hinner den
inte, spelas den snabbare. Inget dras ut i slowmotion. Steg utan ankare spelas
bara i sin vanliga takt efter föregående steg.

Ut i mappen ut/ bredvid plan.json:
  - <nr>-<board>.mp4   ett klipp per fönster (1920x1080, 30 bilder/s, klicken i ljudet)
  - klipp.json         start och slut för varje klipp, för att lägga in dem i Borumi
  - forhandsvisning.mp4  alla klipp på en svart bakgrund med rösten och klicken
"""
import json, os, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright

FPS = 30
SERVER = 'http://127.0.0.1:8765/'
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LJUDMAPP = os.path.join(REPO, 'choosewise', 'ljud')
NIVA = {'landa': 0.35, 'skriv': 0.51, 'lager': 0.22, 'glid': 0.29}
FIL = {'landa': 'klick.wav', 'skriv': 'tangent.wav', 'lager': 'lager.wav', 'glid': 'sus.wav'}

# Läser ut stegens starttider ur tidslinjen: alla tweens, grupperade när de
# startar inom 0,35 s från varandra.
STEG_JS = """() => {
  const tl = tavla.tl, starter = [];
  tl.getChildren(true, true, false).forEach(t => {
    let s = t.startTime(), p = t.parent;
    while (p && p !== tl) { s += p.startTime(); p = p.parent; }
    if (t.duration() > 0.05) starter.push(s);
  });
  starter.sort((a, b) => a - b);
  const steg = [];
  starter.forEach(s => { if (!steg.length || s - steg[steg.length - 1] > 0.35) steg.push(s); });
  return { steg, langd: tl.duration() };
}"""


def tidsfunktion(steg, langd, start, slut, ankare):
    """Ger en funktion: tid i filmen (sekunder) -> tid i boardens tidslinje."""
    # Punkter (filmtid, boardtid) där ett steg ska börja.
    # Ett ankare är antingen en tid (då hör ankare nummer i till steg nummer i)
    # eller {"steg": i, "tid": t} som pekar ut ett visst steg. Ankare som
    # pekar på ett steg som inte finns, eller går bakåt i tiden, hoppas över.
    par = [(a['tid'], a['steg']) if isinstance(a, dict) else (a, i) for i, a in enumerate(ankare)]
    punkter = [(start, 0.0)]
    for v, i in par:
        if i < len(steg) and v > punkter[-1][0] and steg[i] >= punkter[-1][1]:
            punkter.append((v, steg[i]))

    def f(t):
        for (v0, b0), (v1, b1) in zip(punkter, punkter[1:]):
            if t < v1:
                behov, finns = b1 - b0, v1 - v0
                if behov <= finns:                  # tid över: spela, vänta still
                    return min(b0 + (t - v0), b1 - 0.001)
                return b0 + (t - v0) * behov / finns   # för lite tid: snabbare
        v0, b0 = punkter[-1]
        return min(b0 + (t - v0), langd)            # efter sista ankaret: spela klart
    return f


def ljudspar(ljudlista, f, start, slut, ut):
    """Lägger klicken på rätt filmtid och skriver en wav för klippet."""
    langd = slut - start
    cues = []
    for c in ljudlista:
        # Hitta första filmtid då boarden passerar ljudets tid.
        t = start
        while t < slut and f(t) < c['tid']:
            t += 1 / FPS
        if t < slut:
            cues.append((t - start, c['ljud']))
    if not cues:
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i',
                        f'anullsrc=r=48000:cl=stereo', '-t', f'{langd:.3f}', ut], check=True)
        return
    args, filt = ['ffmpeg', '-y', '-loglevel', 'error'], []
    for i, (t, namn) in enumerate(cues):
        args += ['-i', os.path.join(LJUDMAPP, FIL[namn])]
        filt.append(f'[{i}]volume={NIVA[namn]},adelay={int(t * 1000)}|{int(t * 1000)},aresample=48000[a{i}]')
    filt.append(''.join(f'[a{i}]' for i in range(len(cues))) +
                f'amix=inputs={len(cues)}:normalize=0,apad,atrim=0:{langd:.3f}[ut]')
    subprocess.run(args + ['-filter_complex', ';'.join(filt), '-map', '[ut]', '-ac', '2', ut], check=True)


def main(planfil):
    mapp = os.path.dirname(os.path.abspath(planfil))
    plan = json.load(open(planfil, encoding='utf-8'))
    utmapp = os.path.join(mapp, 'ut')
    os.makedirs(utmapp, exist_ok=True)
    relmapp = os.path.relpath(mapp, REPO)
    klipp = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for nr, fon in enumerate(plan['fonster'], 1):
            pg = b.new_page(viewport={'width': 1920, 'height': 1080})
            pg.goto(SERVER + relmapp + '/' + fon['board'])
            pg.wait_for_timeout(800)
            # Bort med startknappen och kamerazonen: de hör bara till förhandsvisningen.
            pg.evaluate("document.querySelector('button')&&document.querySelector('button').remove();"
                        "document.body.classList.add('dolj-kamera')")
            info = pg.evaluate(STEG_JS)
            ljudlista = pg.evaluate("tavla.ljud")
            start, slut = fon['start'], fon['slut']
            f = tidsfunktion(info['steg'], info['langd'], start, slut, fon.get('ankare', []))
            namn = f"{nr:02d}-{os.path.splitext(fon['board'])[0]}"
            print(f"{namn}: {len(info['steg'])} steg, {len(fon.get('ankare', []))} ankare, {slut - start:.1f} s", flush=True)
            with tempfile.TemporaryDirectory() as tmp:
                antal = int(round((slut - start) * FPS))
                for i in range(antal):
                    bt = f(start + i / FPS)
                    pg.evaluate(f"void tavla.tl.pause({bt:.4f}, false)")  # false: kör onUpdate, t.ex. text som skrivs fram
                    pg.screenshot(path=os.path.join(tmp, f'{i:06d}.png'))
                ljudspar(ljudlista, f, start, slut, os.path.join(tmp, 'ljud.wav'))
                ut = os.path.join(utmapp, namn + '.mp4')
                subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS),
                                '-i', os.path.join(tmp, '%06d.png'), '-i', os.path.join(tmp, 'ljud.wav'),
                                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-g', '15',
                                '-c:a', 'aac', '-b:a', '192k', '-shortest', ut], check=True)
                # Kontroll: rätt antal bildrutor.
                n = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0',
                                    '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', ut],
                                   capture_output=True, text=True).stdout.strip()
                if int(n) != antal:
                    sys.exit(f'{namn}: {n} bildrutor, väntade {antal}')
            klipp.append({'fil': 'ut/' + namn + '.mp4', 'start': start, 'slut': slut})
            pg.close()
        b.close()
    json.dump(klipp, open(os.path.join(utmapp, 'klipp.json'), 'w'), indent=2, ensure_ascii=False)

    # Förhandsvisning: svart bild hela filmen, klippen på sina tider, rösten under.
    total = max(k['slut'] for k in klipp) + 1
    args = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i',
            f'color=c=black:s=1920x1080:r={FPS}:d={total:.3f}']
    for k in klipp:
        args += ['-itsoffset', str(k['start']), '-i', os.path.join(mapp, k['fil'])]
    filt, sista, ljud = [], '[0:v]', []
    for i, k in enumerate(klipp, 1):
        filt.append(f"{sista}[{i}:v]overlay=enable='between(t,{k['start']},{k['slut']})':eof_action=pass[v{i}]")
        sista = f'[v{i}]'
        ljud.append(f'[{i}:a]')
    if plan.get('rost'):
        args += ['-i', os.path.join(mapp, plan['rost'])]
        ljud.append(f'[{len(klipp) + 1}:a]')
    filt.append(''.join(ljud) + f'amix=inputs={len(ljud)}:normalize=0[a]')
    subprocess.run(args + ['-filter_complex', ';'.join(filt), '-map', sista, '-map', '[a]',
                           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-c:a', 'aac',
                           '-t', f'{total:.3f}', os.path.join(utmapp, 'forhandsvisning.mp4')], check=True)
    print('klart:', utmapp)


def visa_steg(boardfil):
    """Skriver ut stegens tider i boardens tidslinje, för att välja ankare."""
    rel = os.path.relpath(os.path.abspath(boardfil), REPO)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(SERVER + rel)
        pg.wait_for_timeout(800)
        info = pg.evaluate(STEG_JS)
        for i, s in enumerate(info['steg']):
            print(f'steg {i}: {s:.2f} s')
        print(f"längd: {info['langd']:.2f} s")
        b.close()


if __name__ == '__main__':
    if sys.argv[1] == '--steg':
        visa_steg(sys.argv[2])
    else:
        main(sys.argv[1])
