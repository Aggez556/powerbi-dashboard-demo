# Lokal lednings- och försäljningsrapport

Öppna `Ledningsrapport.pbip` i Power BI Desktop. Den pekar på `LedningsrapportUtanScroll.Report` och den gemensamma `Ledningsrapport.SemanticModel`. Rapporten har fyra sidor: Start, Ledningsöversikt, Försäljningsöversikt och Kunder. Budget och Projekt / beläggning är fortsatt inaktiva navigationsalternativ. I Desktop-redigeringsläge används Ctrl+klick på navigations- och periodknappar.

## Försäljningsöversikt

Sidan följer referensens disposition: sex KPI-kort och fyra native Power BI-visualiseringar på en canvas om 1920 × 1200, visad med FitToPage. Färg och typografi återanvänder projektets tema. Inga företagsnamn eller logotyper visas.

Standardvalet är **R12 september 2026, Alla områden**: 139,5 Mkr omsättning, 36,04 Mkr bruttovinst och 270 köpande kunder. Ledningsöversiktens sparade standardval är också september 2026 enligt den senaste instruktionen. Januari 2023 finns som jämförelseunderlag. Helår erbjuder 2024 och 2025.

Verksamhetsområdet påverkar sidans samtliga mått och jämförelsevärden. De två sista korten byter mellan kunder/omsättning per kund, produktorder/ordervärde respektive debiterade timmar/timpris. Periodtexten använder gemensamma periodmått. Periodbokmärken ändrar bara sina namngivna kontroller, så områdesval och Ledningsöversiktens fasta radfilter behålls.

Visualiseringarna är staplad månadsförsäljning, kategoriers omsättning/marginal i punktdiagram, branschjämförelse och kategori-/artikelmatris. Expandera matrisens kategorier med plusknappen för artikelnivå. R12 och Helår visar periodens månader; Månad visar tolv månaders historik med vald månad markerad. Övriga visualiseringar och kort avser då enbart den valda månaden.

## Kunder

Kunders standard är R12 september 2026, alla branscher. Sex KPI-kort visar aktiva och nya kunder, förlorade kunder, logo churn, revenue churn netto och andel ny-/återaktiverad försäljning. Försäljning per fast periodkohort, kundbrygga, intäktsbrygga och en uppföljningslista visar samma kundidentiteter och transaktioner som övriga sidor.

Bransch påverkar hela sidan; status påverkar bara tabellen. Tabellen visar sju prioriterade kunder utan scrollning. Klicka på en rad för bransch, köpta områden, absolut förändring och hänförlig bruttovinst. Kundmarginal inkluderar hänförliga kostnader; ej fördelad personal finns kvar i områdets resultat. I månadsläget avser kundanalysen R12 till vald månad, uttryckligt angivet i periodtexten. Första tillåtna månad är december 2024 för komplett R12-jämförelse.

Standardkontroller: 240 + 35 + 5 − 10 = 270 kunder. 120,0 − 4,0 − 18,0 + 12,0 + 27,0 + 2,5 = 139,5 Mkr. Logo churn är 4,17 % och revenue churn netto 8,33 %. Detaljer om databerikning och verifiering finns i `_brief/customer-page.md` och `validation/customer-independent-checks.json`.

## Gemensamt underlag

Försäljningsrader har kund, datum, område, artikel, order och debiteringstyp. Artiklar anger kategori och område. Kundbransch ligger i kunddimensionen. Intäkter och direkta kostnader fördelas deterministiskt på kategorier och artiklar med heltalsavrundning som bevarar summorna. Ingen separat hårdkodad KPI-tabell används.

Ordervärdet använder nettointäkten från exakt de produktorder som har positiv försäljning i perioden. Ren kreditkund räknas inte som köpande kund eller positiv produktorder. Timpriset använder endast timdebiterade arbetsraders nettointäkter och timmar; negativa krediterade timmar ingår, medan material och fastpris utesluts. Totalmarginaler och tillväxt räknas från totalbelopp.

För att förena den nya specifikationens föregående kategoriomsättning 73/23/24 Mkr med äldre demodata 73/25/22 Mkr har 2 Mkr intäkt och lika stor direkt kostnad flyttats från teknisk service till bemanning inom föregående R12. Företagets månadsomsättning och resultat samt varje områdes bruttovinst behålls. Septemberkontrollerna för Ledningsöversiktens resultat, budget, uppdrag, kunder och resultatbrygga är bevarade.

## Återskapande och kontroller

Från projektroten, med projektet sparat i Desktop:

```powershell
python scripts/generate-ledningsrapport.py --data-only
python scripts/sales-overview-measures.py
python scripts/customer-measures.py
node scripts/build-sales-overview.cjs
node scripts/build-customer-page.cjs
python scripts/verify-customer-page.py
python scripts/verify-sales-overview.py
python scripts/verify-ledningsrapport.py
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validate-ledningsrapport.ps1
& ./.tools/powerbi/node_modules/.bin/powerbi-report-author.cmd validate powerbi-ledningsrapport/LedningsrapportUtanScroll.Report
```

Datageneratorn anropar automatiskt `extend-sales-overview-data.py`, som i sin tur anropar `extend-customer-data.py` när kundutökningen finns installerad. De separata sidbyggena bevarar Ledningsöversiktens befintliga layout. Kör inte äldre fullständiga rapportgeneratorer för att uppdatera denna version. Parametern `DataFolder` i modellens `definition/expressions.tmdl` ska peka på projektets `data`-mapp. Kundberikningen använder NumPy för balanseringen.

Genomförda kontroller finns i `validation/customer-independent-checks.json` (24 period-/branschfall), `validation/sales-independent-checks.json` (16 period-/områdesfall), `validation/sales-data-enrichment.json`, `validation/data-checks.json` och `validation/tmdl-check.json`. De kontrollerar sparade data, fältbindningar och modellsyntax. `validation/customer-live-check.dax` och `validation/sales-live-check.dax` innehåller frågor för faktisk DAX-kontroll efter import.

**Desktop-kontroll för Kunder:** full import är nu genomförd i Desktop och den uppdaterade datacachen har sparats. `validation/customer-live-verification.json` innehåller verifierade faktiska DAX-resultat, inklusive de exakta standardvärdena och diagrammens summeringar. Ett reserverat DAX-variabelnamn i kundgruppstrenden har rättats. Vid framtida ändring av CSV-filerna krävs en ny Uppdatera och Spara i Desktop. Renderad granskning och senaste preview-resultat redovisas separat i leveransmeddelandet. Ingen PBIX-export eller publicering har genomförts.


## Budget

Budgetscenarier och native resultaträkning finns på sidan **Budget**. Budgetkällan är [data/Budgetscenarier.xlsx](data/Budgetscenarier.xlsx). Se [BUDGET.md](BUDGET.md) för redigering, uppdatering, avstämningar och verifieringsstatus.


Budget är en femte sida i det befintliga projektet [Ledningsrapport.pbip](Ledningsrapport.pbip). Välj Uppdatera för att läsa in Excel-budgeten.
