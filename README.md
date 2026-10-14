# Power BI-rapport med Aubecos design

Det nya fristående projektet finns i **[powerbi-sales-finance/AubecoSalesFinance.pbip](powerbi-sales-finance/AubecoSalesFinance.pbip)**. Det har en startsida med fyra navigationskort, Executive Overview med reproducerbar dummydata och tre förberedda undersidor. Se [anvisningar](powerbi-sales-finance/README.md).

Ett lokalt testprojekt för ett fiktivt handelsföretag är byggt med Aubecos design, reproducerbara dummydata, en Import-modell i TMDL och två rapportsidor i PBIR.

Rapporten ska använda fiktiva data för att demonstrera visualiseringar, nyckeltal och interaktiva filter. Utseendet ska följa Aubecos visuella identitet, med färger, typografi och layout utifrån tillgängligt designunderlag.

## Öppna projektet

Öppna **[powerbi/AubecoHandel.pbip](powerbi/AubecoHandel.pbip)** i Power BI Desktop och välj **Uppdatera**. Läs [öppnings- och laddningsanvisningarna](powerbi/README.md), inklusive nästa steg om Desktop saknas.

Se [valideringsstatus](powerbi/validation/README.md) och [rapportspecifikationen](_brief/report-spec.md). Projektfiler, modellstruktur och CSV-data är kontrollerade. Import, faktisk DAX-körning och rendering har ännu inte kontrollerats i Desktop. Inget har publicerats.

Skills för Taste, semantisk modellering och Power BI-rapportdesign/rapportbygge är installerade lokalt i projektet. Se [installationsstatus](docs/skills-installation.md) och [projektinstruktioner](AGENTS.md).

Aktuell fas är lokal granskning och test i Power BI Desktop.

Den tredje fliken **Budgetplanering** återskapar referensens struktur med Aubecos stil. Se [budgetflikens funktioner och laddningssteg](powerbi/BUDGETPLANERING.md). Budgetberäkningar och filter är en lokal simulering; kommentarsinmatning och skrivfunktioner är visuella platshållare.

Profilanalysen finns i [Aubecos designguide för Power BI](docs/aubeco-powerbi-designguide.md). Ett [schemavaliderat tema](themes/aubeco-powerbi.json) och [hämtad logotypbild](assets/aubeco/aubeco-original.png) finns sparade lokalt. Se [valideringsresultatet](themes/validation-result.json) för kontroller och begränsningar.

## powerbi-dashboard-demo
