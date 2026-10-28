# Ombyggnad: Sirios boards i Choosewise-stil

Den här guiden gäller när en av Sirios 74 boards i `boards/` byggs om till Choosewise-stil i `choosewise/boards/`. Sirios repo är MIT-licensierat, så vi får bygga om fritt. Reglerna kommer från Johans beslut 2026-10-28 och från grafikramverkets Choosewise-regler.

## Facit

De tre godkända proven i `choosewise/prov/` är facit för utseende, kodstil och kommentarer. Läs alla tre innan du bygger något:
- `N1-tidslinje.html` (rörelse längs en linje, fokus som flyttas, bortoning vid kanten)
- `D43-staplar.html` (diagram, exempeldata, fokus med nedtoning, ett klick)
- `N5-ai-chatt.html` (fönster, text som skrivs fram, understrykning i koppar)

## Filen

- Namn: `choosewise/boards/<Sirios id>-<kort svenskt namn>.html`, till exempel `D44-linje.html`.
- Samma skelett som proven: `<link rel="stylesheet" href="../tema.css">`, egen `<style>` för boardens delar, `<div class="cw ljus">`, och sist `<script src="../../skills/board-sync/assets/gsap.min.js">`, `<script src="../spelare.js">` och boardens skript som slutar med `Tavla.start(tl)`.
- Inga andra typsnitt, inga Google Fonts, inga CDN-länkar.
- HTML- och CSS-kommentarer på svenska som förklarar vad varje del gör och varför. Johan är nybörjare och ska kunna läsa och ändra själv. Kommentera avsnitt, inte varje rad.

## Utseende

- **Ljus scen** (`cw ljus`) är standard. Mörk scen (`cw mork`) bara på boards där kamerarutan aldrig syns: kapitelavdelare (D56) och slutbild (X41) får vara mörka.
- **Färger** bara ur `tema.css`: text, dämpad text, accent (djupblå), serierna `--cw-serie-1..3` för diagram med flera serier, och koppar (`--cw-glod`, `--cw-glod-text`, `--cw-glod-sken`) **bara på det som är i fokus**. En sak i fokus åt gången. Det som inte är i fokus tonas ned till 0,38.
- **Typografi:** rubriken som i proven (klassen `.rubrik`, 84 px, tjocklek 300, uppe till vänster vid x 120, y 96). **Ingen text under 42 px**, nyckeltal minst 96 px och tunna (200). Kod och terminal i `var(--cw-font-mono)`, också minst 42 px.
- **Keynote-känsla:** platta ytor, mycket luft, en idé per board. Hellre färre rader, staplar eller kort än små texter. Är Sirios board för tät: förenkla tills allt ryms i 42 px.
- **Ta bort** allt som hör till hans system: kicker-raden, spec-kolumnen till höger, credit-raden, hans kameraruta, gula överstrykningar och prickmönster i bakgrunden.
- **Kamerazonen:** Borumi-rutan ligger nere till höger. **Inget innehåll får ligga där x ≥ 1570 och y ≥ 720** i något viloläge. Använd bredden fram till x 1800 ovanför y 720, och höjden ner till y 1000 till vänster om x 1570.
- Ingen riktig logotyp eller varumärke (inga ChatGPT-, Claude- eller Apple-märken). Generiska fönster, ikoner och enheter.
- Inga fotografier eller videoklipp: Sirios `assets/` med ansikten används inte. Behövs en bild, gör en enkel platshållare (en ruta i `--cw-ljus-alt` med en kort etikett).

## Innehåll

- **Engelska** på boarden (Skool-publiken). Kommentarerna i koden på svenska.
- Exempel ur Johans värld: AI i skolan, lärare, elever, rektorer, promptar, lektioner, bedömning. Behåll Sirios **rörelseidé och boardtyp**, byt hans ämne (priser, API:er, videoproduktion) mot ett skolexempel.
- **Hitta aldrig på fakta.** Siffror är exempeldata och märks med `<div class="exempel">Example data · replace with real numbers and source</div>` som i D43. Historiska fakta bara om de är allmänt kända och säkra.
- Ingen mening längre än ungefär tio ord på boarden.

## Rörelse

- **All rörelse i en GSAP-tidslinje** (`gsap.timeline({ paused: true })`). Inga CSS-animationer (`@keyframes`, `animation:`), ingen `setTimeout`, inga klassbyten i `tl.call`. Exporten hoppar till enskilda bildrutor, så allt måste gå att spola i: fokus och färgbyten görs med tweens (`tl.to(el, { color: ... })`), som i proven.
- Tempot "Lugn": `power2.out`, 0,8 s in, 0,18 s mellan element i en följd.
- **Struktur först:** ramar, axlar och rubrik finns när boarden öppnar, delarna kommer sedan en i taget. Ingenting rör sig efter att det har landat (inga pulser, ingen zoom som fortsätter).
- Boardens totala längd 8–20 s med provtider; synken till Johans röst flyttar tiderna senare.
- Slut med en vila: `tl.to({}, { duration: 2 })`.

## Ljud

Tyst som standard. Enda tillåtna ljudet är `Tavla.ljud(tl, tid, 'landa')`, ett klick, **när ett nyckeltal, ett omdöme eller fokus landar** på boardens viktigaste ögonblick, högst en gång per board. Inget sus, inget tangentljud (Johans val 2026-10-28).

## Kontroll innan en board räknas som klar

1. En lokal server kör på port 8765 i repots rot.
2. Kör `/opt/homebrew/bin/python3.12 -I choosewise/verktyg/stillbilder.py http://127.0.0.1:8765/choosewise/boards/<fil> <scratch>/<id> <3–4 tider>` med tider mitt i uppbyggnaden, vid fokus och i slutvilan.
3. `fel` ska vara tom och varje tid `ok` (ingen krock med kamerazonen).
4. **Titta på varje stillbild** med Read: ingen text avklippt vid kanten, inget överlapp, inget under 42 px, luft runt allt, fokus syns.
5. Rätta och kör om tills allt är rent.
