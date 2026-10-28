---
name: choosewise-board-synk
description: Synkar Choosewise-boards till Johans röst och exporterar dem som klipp att lägga i Borumi. Steg 3 av 3 i Choosewise-boardsflödet (plan → boards → synk). OPT-IN: använd BARA när Johan uttryckligen nämner "choosewise-board-synk", "board-synk", "synka boardsen" eller "/choosewise-board-synk". Starta inte på generella ord som video, export, rendera eller redigera; videostudio, grafikramverket och andra verktyg är egna system.
---

# Choosewise board-synk

Tar en godkänd `plan.json` och boardsen i `choosewise/film-<namn>/` och gör ett MP4-klipp per board där varje steg landar på sitt ord.

Repot: `~/Projekt/choosewise-boards`.

## Köra

1. Server i repots rot: `python3 -m http.server 8765`.
2. `/opt/homebrew/bin/python3.12 -I choosewise/verktyg/synk.py choosewise/film-<namn>/plan.json`
3. Ut i `choosewise/film-<namn>/ut/`:
   - ett klipp per board (1920×1080, 30 bilder/s, klicken i ljudet)
   - `klipp.json` med start och slut för varje klipp
   - `forhandsvisning.mp4` med alla klipp, rösten och klicken

Hur tiden räknas: stegen hittas i boardens GSAP-tidslinje. Mellan två ankare spelas boarden i normal fart och väntar sedan still på nästa ord; hinner den inte spelas den snabbare. Ingen slowmotion. Steg utan ankare följer i sin vanliga takt.

## Kontroll innan Johan ser den

- Skriptet stoppar om ett klipp får fel antal bildrutor.
- Ta stillbilder ur `forhandsvisning.mp4` strax före och strax efter varje ankare (`ffmpeg -ss <tid> -i … -frames:v 1`) och titta: inget får synas före sitt ord.
- Låt Johan titta på förhandsvisningen innan klippen läggs in.

## Lägga in i Borumi

Med Johans godkännande: följ `videostudio`-skillens sätt att arbeta i Borumi (läs Borumis guider först). Importera varje klipp och lägg det som `media_overlay` i helbild på tiden i `klipp.json`. Borumis kameraruta ligger ovanpå och boardsen lämnar den zonen tom. Klippens klick följer med i deras ljud.

## Ljudfilerna

Klicken läses från `choosewise/ljud/` (gitignorerad: köpt ljudpaket, publikt repo). Saknas mappen: kopiera från `~/Projekt/AI-OS/brands/choosewise/ljudkit/`.
