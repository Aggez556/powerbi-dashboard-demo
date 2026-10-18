# Gemensam formatering

Rapporten behåller befintliga sidlayouter och färgprofil. Kör `node scripts/harmonize-report-design.cjs` som sista formateringssteg efter sidgeneratorerna.

- Sidrubriker på analyssidor: 30 pt.
- Panel- och diagramrubriker: 18 pt, Segoe UI Semibold.
- KPI-rubriker: 13 pt. Sexkortsradernas huvudvärden: 30 pt. Budgetens tre större kort behåller 36 pt.
- Legender: 11 pt. Befintlig kompakt gruppering behålls.
- Primär text: #0F3163. Sekundär text: #5B6B80.
- Positivt utfall: #007956. Negativt utfall: #B42318. Separata färger för dataserier och värmekartor behålls.
- Startsidan behåller sin större introduktionstext och sina navigationskort; den har ett annat syfte än analyssidorna.
- Tabeller, axeltexter och fotnoter behåller storlekar anpassade till tillgängligt utrymme.

Ändringslistan för körningen finns i `validation/design-consistency.json`. Detta är en filgranskning; visuell kontroll i Power BI Desktop krävs också.
