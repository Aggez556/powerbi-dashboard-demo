# Kundhistorik i demonstrationen

## Senaste förbättring: ojämnt kundbeteende

Efter stegvis historik och fördelade kundstarter körs `scripts/randomize-customer-behaviour.py`. Ett fast slumpfrö ger olika antal kundstarter mellan månader, olika köpstorlekar och datum, mer varierad branschfördelning och individuella kostnadsandelar. Fröet gör datan stabil mellan uppdateringar. Kundstarter följer inte längre ett schema med lika många per månad, och beloppen i nya transaktioner är inte lika stora.

Månadssummor för intäkter och debiterade timmar per verksamhetsområde, artikel och debiteringssätt samt kostnader per kostnadstyp bevaras. Kund- och branschfördelning samt kundmarginaler och churn räknas däremot om från den nya historiken. Äldre referensfördelningar längre ned är historiska. Aktuella resultat finns i customer-independent-checks.json och customer-live-verification.json. Diagrammet heter nu Omsättning per kundgrupp (Mkr), eftersom decimalerna avser miljoner kronor. Kundantal beräknas som heltal, och även detta kontrolleras mot faktisk DAX.

## Senaste förbättring: löpande kundstarter

`scripts/spread-customer-acquisition.py` körs efter historikberikningen och sprider nya kundstarter över samtliga månader 2024 och 2025 samt januari–september 2026. Återaktivering sker vid separata tillfällen under 2025 och 2026. Detta ersätter det tidigare antagandet att alla 35 nya och 5 återaktiverade kunder börjar köpa i oktober 2025.

Kundernas periodstatus beräknas fortfarande från transaktionerna. Därför ändras kundfördelning, churn och intäktsbryggans delbelopp när kundstarterna flyttas mellan jämförelseperioderna. De gamla exakta standardvärdena i beskrivningen nedan är historiska, inte längre mål för datan. Omsättning, kostnader, rörelseresultat, debiterade timmar och branschfördelning bevaras på månadsnivå. R12 har fortsatt 270 aktiva och 10 förlorade kunder, men nu 257 tidigare, 20 helt nya och 3 återaktiverade. Kontrollera aktuella värden i customer-independent-checks.json och customer-live-verification.json.

Köphistoriken innehåller nu historiskt kundbortfall även i helåren 2024 och 2025. De tidigare oanvända kundnycklarna 281–300 används för äldre kundrelationer med olika slutdatum. Standardperioden R12 oktober 2025–september 2026 behåller sina 270 aktiva kunder, 240 tidigare kunder, 35 helt nya, 5 återaktiverade och 10 förlorade kunder. Referensperiodens intäkter per kund och dess intäktsbrygga är oförändrade.

Köpdatumen sprids deterministiskt inom respektive månad. De förlorade kundernas senaste köp ligger därför på olika datum och flera månader. Transaktioner och hänförliga kostnader omfördelas konsekvent. Kontroller bevarar intäkter och debiterade timmar per månad, verksamhetsområde, artikel, debiteringssätt och kundbransch samt kostnader per månad, verksamhetsområde, artikel och kostnadstyp. Första köp uppdateras från den nya historiken, medan uttrycklig historik före dataperioden bevaras.

Detta är fortfarande syntetisk demonstrationsdata, inte ett statistiskt representativt kundbeteende. Inga procentsatser slumpas i visualen: kundstatus och avvikelser beräknas från de faktiska demotransaktionerna.

Implementering: `scripts/realistic-customer-history.py`. Körs efter grundgenerering och `extend-customer-data.py`, före ny import och verifiering. Skriptet är idempotent för den befintliga dataversionen via markören i data/manifest.json; kör inte den äldre grundberikningen direkt på redan berikade data. Vid full omgenerering ska grunddata och manifest återställas tillsammans innan denna sista berikning körs.

Verifiering finns i validation/customer-history-realism.json och validation/customer-independent-checks.json. En riktad Desktop-uppdatering kan göras med scripts/refresh-customer-history.ps1. Annars välj Uppdatera i Power BI Desktop.
