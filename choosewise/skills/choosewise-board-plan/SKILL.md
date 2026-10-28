---
name: choosewise-board-plan
description: Planerar vilka Choosewise-boards en inspelad film behöver och vilket ord varje steg ska landa på. Steg 1 av 3 i Choosewise-boardsflödet (plan → boards → synk). OPT-IN: använd BARA när Johan uttryckligen nämner "choosewise-board-plan", "board-plan", "planera boards" eller "/choosewise-board-plan". Starta inte på generella ord som grafik, slides, animation, video eller förklarfilm; grafikramverket, motion-os och andra stilar är egna system.
---

# Choosewise board-plan

Du läser transkriptet av en inspelad film och bestämmer **vad** som ska visas: vilka repliker som behöver en board, vilken board ur katalogen som passar, vad som ska stå på den och vilket ord varje steg landar på. Utseendet bestäms inte här (det är `choosewise-boards`), och inget renderas (det är `choosewise-board-synk`).

Metoden bygger på Sirio Beratis skill `explainer-board-brief` (MIT, finns i repots `skills/`), anpassad till Johans flöde: han spelar in i Borumi och pratar till sin gamla Keynote-grafik, och boardsen läggs på i efterhand.

Repot: `~/Projekt/choosewise-boards` (`choosewise/` är Johans del).

## Det du behöver

1. **Filmens namn** och var den finns: ett Borumi-projekt, eller en ljud-/videofil.
2. **Ordtider.** Hämta transkriptet med ord och tider ur Borumi (`get_transcript` på projektet; läs Borumis guider först enligt dess MCP-instruktioner). Finns inget Borumi-projekt: kör `whisper <fil> --model base --language en --word_timestamps True --output_format json`.
3. **Fakta.** Siffror och påståenden på boardsen ska komma från det Johan säger eller från en källa han anger. Saknas något: skriv `[BEHÖVS: …]` och fråga. Hitta aldrig på.

## Metoden

1. **Numrera replikerna** (R1, R2 …) med start- och sluttid ur transkriptet.
2. **Bedöm varje replik:** BOARD (något tittaren inte kan hålla i huvudet bara genom att lyssna: en term, ett tal, en jämförelse, en process, ett citat, ett påstående som behöver belägg, ett exempel), SAMMA BOARD (fortsätter bilden som redan syns) eller KAMERA (Johan pratar till tittaren; ett medvetet val, inte en lucka). Skriv för varje BOARD en mening om vad tittaren ska ha förstått efteråt.
3. **Gruppera** repliker som delar bild till en board. En board är en bild. Ny board när bilden byts. Återkommande ankarbild (t.ex. WISE) byggs en gång och kommer tillbaka.
4. **Välj board** ur `choosewise/katalog.md` genom att matcha "say it when" mot replikerna. Hellre ett nytt steg på samma board än en ny board. Ingen board över ungefär 60 s utan nytt steg.
5. **Fyll innehållet:** rubrik (påståendet), etiketter, siffror med källa. Exempeldata-märket tas bort när riktiga siffror med källa finns; annars står det kvar eller boarden byts.
6. **Ankare:** för varje steg i boarden, det exakta ordet ur transkriptet som det ska landa på, med tid. Stegen listas med `/opt/homebrew/bin/python3.12 -I choosewise/verktyg/synk.py --steg choosewise/boards/<fil>` (server på port 8765 i repots rot). Ett namngivet ting landar på sitt namn, ett tal på talet.
7. **Kontroll:** inget fönster överlappar ett annat; varje board öppnar på första ordet i sitt block; inget tal på en board motsäger det Johan säger.

## Leverans

Skapa mappen `choosewise/film-<namn>/` och skriv:
- `plan.md`: en tabell per board (tid, board, varför, innehåll som ändras, ankare ord → tid) och listan med `[BEHÖVS]`. Det är den Johan godkänner.
- `plan.json` i formatet som `synk.py` läser (se `choosewise-board-synk`), med ankare som `{"steg": i, "tid": t}`.

Visa planen för Johan och vänta på hans godkännande innan boardsen byggs.
