# Ledningsrapport – lokalt Power BI-projekt

Öppna `Ledningsrapport.pbip` i Power BI Desktop. Projektet har en lokal Import-modell och exakt två sidor: **Start** och **Ledningsöversikt**. Välj **Uppdatera** vid första öppningen för att läsa CSV-filerna. Vid fråga om sekretessnivå kan de lokala demodatafilerna klassas som offentliga. Inga externa datakällor eller publicering används.

Start återanvänder Sales Finance-projektets portalprincip: ljus sandfärgad bakgrund, mörkblå rubriker, vita navigationskort och orange betoning. Ledningsrapport är organisationen i denna rapport; Aubecos befintliga färger och Power BI-typsnitt används som designinspiration. Ledningsöversikt följer referensbildens disposition med sidonavigation, sex KPI-kort och ett rutnät med fyra analysytor.

## Perioder och navigation

- Standard: R12 oktober 2025–september 2026; jämförelse oktober 2024–september 2025.
- R12 erbjuder december 2024–september 2026 som slutmånader.
- Helår erbjuder 2024 och 2025 med kompletta föregående år.
- Månad erbjuder januari 2024–september 2026. Trenddiagrammen visar tolv månaders historik och vald månad markeras med mörk orange stapel.
- Periodknapparna använder bokmärken som byter periodläge och visar rätt datumväljare. Byte av läge återställer periodväljaren till det senaste kompletta alternativet.
- Start och Ledningsöversikt har sidnavigation. De övriga fyra områdena är inaktiva och har inga rapportsidor.
- I Desktop-redigeringsläge används Ctrl+klick på navigations- och bokmärkesknappar.

Alla KPI-värden, jämförelser, trendserier, områdestabellen och bryggan är modellmått. Den inbyggda vattenfallsvisualen räknar sin slutstapel; dess slutetikett anges av ett dynamiskt mått. Ekonomiska belopp är redan femdubblade jämfört med referensbilden. Marginaler och volymer har inte skalats.

## Modell och demodata

14 tabeller, 10 enkelriktade relationer och 68 DAX-mått. Datum, kunder och verksamhetsområden filtrerar faktatabeller för försäljning, direkta kostnader, gemensamma kostnader, uppdrag och månadsbudget. Frikopplade period- och trendtabeller gör att Månad kan visa historisk kontext utan att ändra KPI-perioden.

Data täcker januari 2023–september 2026. Intäkterna innehåller kreditnotor; kund 301 har endast krediter och räknas inte som aktiv. Direkta kostnader inkluderar ej uppdragsfördelad personal. Gemensamma kostnader inkluderar avskrivningar. Uppdrag har stabila unika identiteter och avbokade uppdrag exkluderas. Kundantalet räknas unikt över områden.

`DataFolder` i `Ledningsrapport.SemanticModel/definition/expressions.tmdl` pekar på projektets lokala `data`-mapp. Ändra parametern om projektet flyttas.

Återskapa från projektroten:

```powershell
python scripts/generate-Ledningsrapport.py
node scripts/build-Ledningsrapport.cjs
python scripts/verify-Ledningsrapport.py
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validate-Ledningsrapport.ps1
& ./.tools/powerbi/node_modules/.bin/powerbi-report-author.cmd validate powerbi-ledningsrapport/Ledningsrapport.Report
```

Rapportbygget är avsett för det genererade projektet. Manuell redigering i Desktop ska sparas innan en ny generering; skripten återställer de genererade definitionerna.

## Verifiering

- `validation/data-checks.json`: oberoende beräkningar från sparade CSV-filer; standardbelopp, fyra periodfall, budget, kundöverlapp, uppdrag, resultatbrygga, referensintegritet och visuella fältbindningar kontrollerade.
- `validation/tmdl-check.json`: Microsoft TOM har läst hela TMDL-modellen utan syntaxfel.
- `validation/desktop-check.dax`: frågor för faktisk kontroll av periodmått, standardbelopp och bryggan i en laddad Power BI-modell.
- `validation/report-schema.json`: rapportverktygets schemaresultat när valideringen körts.

CSV-kontroller och TMDL-inläsning ersätter inte faktisk Import, DAX-körning och visuell granskning i Desktop. Dessa kräver att den nya rapporten kan laddas i den lokala Desktop-värden. Slutstatus för den kontrollen redovisas i chatten; skärmbilder räknas endast som verifiering om de kommer från den laddade Power BI-rapporten. Ingen PBIX eller skärmbild påstås levererad utan faktisk export eller fångst.

Specifikationen finns i `_brief/report-spec.md` och layoutmåtten i `validation/layout.json`.
