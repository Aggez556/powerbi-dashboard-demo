# Gemensamma tooltips

Kundsidans godkända pilot ligger till grund för övriga rapportsidor. `scripts/design-report-tooltips.cjs` tillämpar ändringarna utan att ändra modell eller faktadata.

| Sida | Anpassning |
| --- | --- |
| Start | Inga datadiagram eller datatooltips att ändra. Navigering behålls. |
| Ledningsöversikt | Tre diagram med svenska visningsnamn, Segoe UI 11, marinblå värden, grå etiketter och vit ogenomskinlig bakgrund. |
| Försäljningsöversikt | Månadsförsäljningen använder en dold tooltip-sida med verksamhet, månadens försäljning och samma månad föregående år i Mkr. Punkt- och branschdiagrammen använder gemensam standardstil. Produktanalysens Vega-tooltips visar strukturerade uppgifter om post, verksamhet, jämförelse eller hovrat nyckeltal. |
| Budget | Vega-celler visar post, period, jämförelse och värde som separata fält. Avvikelser visar även att plus är bättre och minus sämre. Kortens synliga förklaringar behöver inga dubblerade tooltips. |
| Uppdrag / beläggning | Gemensam standardstil för diagram och tabeller. Korta svenska namn för tidsslag och debiteringsgrad. Generella timmar/kapacitet har tagits bort ur tooltipen för de två debiteringsgradslinjerna eftersom de inte beskriver den enskilda linjen. |

KPI-kortens dubblerade standardtooltips är avstängda. Sidfilter och reglage behåller sina funktioner. Inga procenttal summeras i tooltip-tabellerna.

Den egna försäljningstooltipen är markerad med både sidtypen `Tooltip` och tooltip-bindning och är dold i läsvyn. Filterkontext överförs från källdiagrammet. Formatkontroll ersätter inte faktisk hovring i Power BI Desktop; utseende och kontext måste granskas där.
