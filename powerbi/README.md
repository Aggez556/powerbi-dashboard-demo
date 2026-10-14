# AubecoHandel – lokalt Power BI-testprojekt

En tredje flik, **Budgetplanering**, finns nu med referensbildens struktur. Läs [funktioner, demonstrationsbegränsningar och laddningssteg](BUDGETPLANERING.md). De två ursprungliga sidorna och Aubecos tema är bevarade.

Öppna **[AubecoHandel.pbip](AubecoHandel.pbip)** i en aktuell Power BI Desktop för Windows. Projektet innehåller en Import-modell i TMDL, två rapportsidor i PBIR och lokala CSV-filer. Inget har publicerats.

## Öppna och ladda

1. Installera Power BI Desktop om det saknas: [Microsofts installationsanvisning](https://learn.microsoft.com/power-bi/fundamentals/desktop-get-the-desktop). Använd vanliga Desktop, inte Report Server-versionen.
2. Om din version kräver förhandsfunktioner: **Arkiv → Alternativ och inställningar → Alternativ → Förhandsfunktioner**. Aktivera Power BI Project (.pbip) och förbättrat rapportformat (PBIR) om alternativen visas. Starta om Desktop. Se [Microsofts PBIP-dokumentation](https://learn.microsoft.com/power-bi/developer/projects/projects-overview) och [PBIR-dokumentation](https://learn.microsoft.com/power-bi/developer/projects/projects-report).
3. Öppna `C:\dev\codex-labb\powerbi\AubecoHandel.pbip`.
4. Välj **Start → Uppdatera** för att läsa in de fyra lokala CSV-filerna. Ingen datacache levereras. Om en fråga om lokala datakällor visas, kontrollera sökvägarna och godkänn inläsningen.
5. Om projektet flyttas: välj **Transformera data → Hantera parametrar** och ändra `DataFolder` till den nya absoluta sökvägen till `powerbi/data`. Välj **Stäng och använd**, därefter **Uppdatera**. Den levererade parametern är `C:/dev/codex-labb/powerbi/data`.

Desktop hittades inte via standardinstallationsväg, Store-paket eller PATH vid byggtillfället. Första konkreta nästa steg är därför installation enligt länken ovan, följt av steg 3–4. MCP behövs inte för att öppna projektet och läsa CSV-filerna. En anslutning till en körande Desktop-modell behövs däremot om Codex senare ska köra DAX och kontrollera modellen automatiskt.

## Innehåll och användning

| CSV | Rader | Namn i modellen |
|---|---:|---|
| FactSales | 10 000 | Försäljning |
| DimDate | 731 | Datum |
| DimCustomer | 100 | Kunder |
| DimProduct | 30 | Produkter |

Försäljningen omfattar 4 000 unika order med två eller tre rader, fördelade över 2024–2025. Fem kategorier har sex produkter vardera. Fast slumptalsfrö `20261006` ger reproducerbara fiktiva data. Vikter ger starkare november–december, svagare semesterperiod, färre helgorder och högre försäljning 2025. Produktpriser, rabatter och kostnadsandelar varierar; bruttomarginal beräknas som sammanlagd bruttovinst dividerad med omsättning.

Modellen har tre aktiva relationer från dimensionernas unika nycklar till Försäljning, många-till-en och enkelriktad filtrering från dimension till faktatabell. Datum är markerad via TMDL:s `dataCategory: Time` och unik datumkolumn med `isKey: true`. Kalendern omfattar även skottdagen. Tekniska nycklar och råa beloppskolumner är dolda; använd de svenska måtten.

**Försäljningsöversikt:** fem KPI-kort, månadsutveckling, tio största kunder samt år- och kategorifilter. **Produktanalys:** omsättning och marginal per kategori, tio största produkter samt tabell med samtliga produkter. Sidflikarna ger navigation. Filter är separata per sida, med 2025 som startval. Diagram och kort använder inbyggda visualiseringar.

Tillväxt kräver ett enskilt valt år. För 2024 visas tomt eftersom 2023 saknas. Om båda åren väljs visas också tomt i tillväxtkortet. Orderantal per kategori är inte additiva: en order kan innehålla flera kategorier. Belopp är i SEK och inkluderar ingen särskild momsberäkning.

Designen följer [Aubecos designguide](../docs/aubeco-powerbi-designguide.md): marinblå hierarki, ljus sandfärgad bakgrund, vita visualytor, diskret orange accent och Segoe UI. Rapporten registrerar en lokal kopia av [temat](../themes/aubeco-powerbi.json). Tre kortspecifika temaobjekt (`border`, `padding`, `spacing`) utelämnas i kopian för kompatibilitet med CLI:s visualmetadata; padding och spacing anges direkt på korten. Färger och typografi bevaras.

## Kontroll i Desktop

Efter uppdatering, kontrollera att inga visualer visar fel och att år/kategori filtrerar båda sidorna. Kontrollera datumtabellens markering och de tre relationerna i modellvyn. Kontrollera att månadsaxeln är kronologisk, att Top 10-listorna sorterar fallande och att produkttabellen går att rulla. Granska även kortens etiketter, procentformat, kontrast och layout vid sidpassning.

Utan kategorifilter och med 2025 valt ska dessa **oberoende beräknade förväntade värden** visas, eventuellt avrundade i kort:

| Mått | Förväntat 2025 |
|---|---:|
| Omsättning | 13 818 582,35 kr |
| Kostnad | 10 388 591,37 kr |
| Bruttovinst | 3 429 990,98 kr |
| Bruttomarginal | 24,8 % |
| Antal order | 2 171 |
| Tillväxt mot föregående år | 19,2 % |

Kör [check-measures.dax](validation/check-measures.dax) i Desktop-vyn för DAX-frågor och jämför med [förväntade värden](validation/data-and-measure-expectations.json). Dessa förväntningar har räknats i Python/SQLite; DAX har ännu inte körts i Analysis Services. Fullständig [valideringsstatus](validation/README.md) skiljer dessa kontroller åt.

## Återskapa och validera

Kör från `C:\dev\codex-labb`, med Desktop stängt för att undvika att det skriver över filändringar. Generatorerna skriver över levererad data, modell och rapportlayout; spara egna ändringar först.

```powershell
python scripts/generate-sales-project.py
node scripts/build-sales-report.cjs
node scripts/build-budget-page.cjs
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/validate-tmdl.ps1
python scripts/verify-sales-data.py
python scripts/verify-budget-page.py
& ./.tools/powerbi/node_modules/.bin/powerbi-report-author.cmd --out powerbi/validation/pbir-result.json validate powerbi/AubecoHandel.pbip
```

Python använder standardbiblioteket. Rapportverktyget finns i `.tools/powerbi`; dess npm-beroenden kan återställas med `npm ci --prefix .tools/powerbi`. Microsofts TOM-bibliotek finns lokalt i `.tools/tom` och kan vid behov hämtas igen med `python scripts/fetch-tom.py`. Schemahämtning kräver internet. Processens `ExecutionPolicy Bypass` möjliggör bara den aktuella valideringskörningen, utan permanent ändring av Windows-inställningar.
