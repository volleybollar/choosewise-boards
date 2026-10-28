---
name: choosewise-boards
description: Choosewise-boardsens utseende, rörelse och katalog (142 animerade förklarboards i HTML + GSAP), och hur en board anpassas till en film eller byggs ny. Steg 2 av 3 i Choosewise-boardsflödet (plan → boards → synk). OPT-IN: använd BARA när Johan uttryckligen nämner "choosewise-boards", "choosewise boards", "boardsen" i den här betydelsen eller "/choosewise-boards". Starta inte på generella ord som grafik, slides, animation eller video; grafikramverket, motion-os och andra stilar är egna system och blandas aldrig in.
---

# Choosewise boards

Repot: `~/Projekt/choosewise-boards` (en fork av Sirio Beratis YouTube-AI-Motion-Graphics, MIT). Johans del ligger i `choosewise/`.

## Filerna

| Fil | Vad |
|---|---|
| `choosewise/katalog.md` | Alla 142 boards: syfte, "say it when", scen, ljud, vad som måste bytas |
| `choosewise/boards/` | Boardsen. `index.html` är galleriet, `../oversikt.jpg` alla på en bild |
| `choosewise/OMBYGGNAD.md` | **Reglerna** för utseende, innehåll, rörelse, ljud och kontroll. Läs före varje ändring |
| `choosewise/tema.css` | Färger, typsnitt, storlekar (ur grafikramverkets Choosewise-stil) |
| `choosewise/spelare.js` | Förhandsvisning: startknapp, K visar Borumi-rutan, ljudlistan för exporten |
| `choosewise/verktyg/stillbilder.py` | Kontroll: stillbilder, JS-fel, kamerazonen |
| `choosewise/prov/` | De tre första godkända proven (facit) |

Förhandsvisning: `python3 -m http.server 8765` i repots rot, öppna `http://127.0.0.1:8765/choosewise/boards/index.html`.

## Det viktigaste ur reglerna

- Ljus scen är standard; mörk bara där Borumi-rutan inte syns (Johans blå bakgrund).
- Inget innehåll där x ≥ 1570 och y ≥ 720: där ligger Borumi-rutan.
- Text minst 42 px. Koppar bara på det som är i fokus, en sak åt gången.
- All rörelse i en GSAP-tidslinje som går att spola; inga CSS-animationer.
- Tyst som standard; bara ett klick när det viktigaste landar.
- Engelska på boarden. Hitta aldrig på fakta; exempeldata märks.

## Anpassa en board till en film

1. Kopiera boarden från `choosewise/boards/` till filmens mapp `choosewise/film-<namn>/` (samma djup, så att `../tema.css` fungerar; boards med `media/` behöver mappen kopierad eller sökvägen ändrad).
2. Byt innehåll enligt planen: rubrik, etiketter, siffror med källa. Ta bort exempeldata-märket bara när siffrorna är riktiga och källan står på boarden.
3. Behåll rörelsen och stegen; ankarna i planen pekar på stegen.
4. Kontrollera med `stillbilder.py` och titta på bilderna. Visa Johan innan synk.

## Bygga en ny board

Följ `OMBYGGNAD.md` och utgå från en board i katalogen som liknar. Lägg den i `choosewise/boards/`, lägg till en rad i `katalog.md`, kör kontrollen och bygg om galleriet och översiktsbilden.
