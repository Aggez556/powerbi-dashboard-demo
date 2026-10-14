# Budgetplanering

Den tredje fliken följer den bifogade referensens struktur: vänsterspalt med scenario, version, år och månad; fyra paneler upptill; bred resultatmatris nedtill. Färger, typsnitt och lugna ytor följer Aubecos befintliga tema. De två tidigare sidornas filer och temat har inte ändrats.

## Funktioner

- Scenario BU 5/BU 6 ger budgetfaktor 1,05/1,08.
- Procentjustering simulerar förändring mot föregående år, med 3 % som utgångsvärde.
- Fördelning kan vara jämn över året eller följa föregående års säsongsvariation. Ett valt årsbelopp fördelas ovanpå budgetbasen.
- Version väljer Actuals, Actuals PY, Max YTD PY eller Budget i utfallskolumnen. Budgetkolumnen visar alltid planeringen.
- År och månad filtrerar resultatmatrisen. Status filtrerar exempelkommentarerna.
- Matrisen visar budget och utfall per månad samt intäkter, kostnader och rörelseresultat.

Nettoomsättning och varukostnad i Actuals kommer från befintliga försäljningsdata. Övriga intäkter är simulerade som 4 % av omsättningen, externa kostnader 8 %, personal 12 % och avskrivningar 3 %. Budgetens varukostnad är 73 % av planerad omsättning. Dessa är demonstrationsantaganden, inte en faktisk bokföring. För 2024 används aktuellt års försäljning som budgetbas eftersom 2023 saknas; PY-utfall för 2024 saknas.

Månadsuppdateringens beloppsfält, ny kommentar och ✓/× är visuella platshållare. De är inte inmatningskontroller eller knappar för att spara, radera eller återställa. Slicervalen beräknar en lokal simulering och skriver inte tillbaka data. En full skrivfunktion som i referensen kräver ytterligare teknik och är inte implementerad i denna lokala PBIR-demonstration.

## Öppna efter ändringen

Nya fristående Import-tabeller och mått har lagts till i TMDL. Stäng den tidigare öppna Desktop-versionen utan att spara över de nya projektfilerna. Öppna `AubecoHandel.pbip` igen och välj **Start → Uppdatera**, så att även budgettabellerna läses från samma DataFolder. Välj fliken **Budgetplanering**. Ingen publicering behövs.

Kontrollera att BU 5/BU 6, justering och fördelning ändrar budgetkolumnen, att datumval filtrerar rätt och att tabellens månadshierarki visas. Om endast år syns, använd matrisens **Utöka alla ned en nivå** för att visa månaderna. Matrisen ska rulla horisontellt liksom referensen. Granska också textklippning och slicerns numeriska reglage i den aktuella Desktop-versionen.

## Filer och kontroller

`scripts/build-budget-page.cjs` skapar endast budgetfliken, de sju budgettabellerna och dess nya mått. Tidigare sidor och tema kontrolleras med SHA-256 före/efter. `validation/budget-page.json` innehåller layout, bindningar och begränsningar. `validation/budget-pbir-result.json` innehåller aktuell PBIR-kontroll. Microsoft TOM används för TMDL-deserialisering; detta kör inte DAX eller Power Query.

För att återskapa hela projektet, kör budgetbyggaren **efter** de två befintliga generatorerna. Att köra bara den gamla rapportgeneratorn tar bort budgetfliken ur sidordningen; den läggs tillbaka av budgetbyggaren. Stäng alltid Desktop innan generatorer körs.

```powershell
python scripts/generate-sales-project.py
node scripts/build-sales-report.cjs
node scripts/build-budget-page.cjs
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/validate-tmdl.ps1
```

Visuell likhet, exekverad DAX och ny inläsning behöver kontrolleras i Desktop; filkontroll innebär inte pixelverifierad 1:1-återgivning.

Efter rapporterat matrisfel har budgetmåttens DAX rättats och **körts i den faktiska öppna Desktop-motorn**. Utfall och budget har jämförts med oberoende dataförväntningar. Se [felorsak och validering](validation/budget-fix.md). De nya filernas visuella återgivning återstår att granska.
