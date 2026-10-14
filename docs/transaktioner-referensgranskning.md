# Transaktioner – referensgranskning

Referens: användarens Transaction Details-bild, anpassad till Aubecos svenska rapport.

## Komponentinventering och resultat

- Sidhuvud, logotyp och navigation: befintliga komponenter bevarade. Rubrik Transaktioner, introduktion om försäljning och lönsamhet per orderrad.
- Periodfilter: gemensamma Månad och År från den färdiga Försäljningsanalysen. Ersätter referensens datumintervall enligt användarens instruktion.
- KPI-rad: sammanhängande vitt kort med fem delar, tunna blå vänstermarkeringar och runda ikoner. Omsättning, sålda enheter, bruttovinst, bruttomarginal och leveranser. Rubriker 15 pt, huvudvärden 28 pt, inga sparklines eller jämförelseetiketter eftersom referensen saknar dem.
- Detaljkort: stort vitt kort med rubrik till vänster och fungerande native produktsökning till höger. Sökoperator kan väljas i kontrollen.
- Tabell: datum, säljare, team, marknad, kategori, produkt, enhetspris, antal, varukostnad, omsättning, bruttovinst, marginal och kompakt Rad-ID. Numeriska värden högerställda; svenska talformat. 9 pt som andra färdiga tabeller, diskreta radlinjer. Hela bredden används, inga horisontella scrollister i granskade kontexter. Vertikal scrollbar är avsiktlig.
- Positiv/negativ bruttovinst och marginal har grön/röd villkorsstyrd text. Marginalen har native datastaplar med separat högerställd procenttext.

## Datakontroll

Ingen dataregenerering eller ändring av affärsmåtten. Ett dolt presentationsmått, Transaktion marginalspår, har tillkommit. TOM-validering: nio Import-tabeller, fyra korrekta enkelriktade relationer.

Actual Desktop DAX och oberoende CSV-kontroller verifierar sex kontexter: helår 2025, oktober, januari–mars, oktober/Norge, produktsökning Hantel och tom produktkontext. Radantal, omsättning, kostnad, vinst, viktad marginal, antal enheter och distinkta order/leveranser matchar.

Fem individuella orderrader jämförda med faktakällan och dimensionerna: datum, rad/order-ID, säljare, team, land, kategori, produkt, enhetspris, antal och belopp matchar. Rad-ID behåller korrekt detaljnivå och förhindrar sammanslagning av likadana orderrader.

## Faktisk bild- och interaktionskontroll

Färska CLI Desktop-bilder öppnade och granskade för helår, oktober, januari–mars, oktober/Norge och tomt resultat. Separat bild av själva interagerade Desktop-fönstret visar produktsökningen Hantel och korrekt filtrerade KPI-värden (809 enheter, 179 leveranser, marginal 32,1 %). Sökning och rensning bekräftade genom faktisk UI-interaktion. Numerisk sortering bekräftad i renderade rader.

Periodkombinationerna verifierades med explicit filterkontext och bildgranskning, inte som godkända klicktester på månadslistan.

## Konkreta avvikelser och begränsningar

- Eftergranskning: marginalspåren är nu rundade SVG-bilder med grå bakgrund och centrerad nollpunkt. Procenten ligger i en separat numerisk kolumn (%) för korrekt sortering.
- Extra Rad-ID-kolumn krävs för säker detaljnivå och stabil sortering.
- Befintliga data saknar negativa vinstrader i kontrollerade perioder. Negativ färg och negativa datastaplar är definierade men har inte observerats med verkliga negativa data.
- Försök med ScrollPattern, mus och tillgänglighetsgrid kunde inte bekräfta att sista raden nås automatiskt. Inbyggd vertikal scroll är kvar; ingen godkänd sista-raden-interaktion påstås.
- PBIR-validering: noll fel, en befintlig varning för otillgängligt 2.13.0-schema i Desktop-serialiserade komponenter.

Slutläge: 2025, alla månader, tom produktsökning, inga tillfälliga sidfilter. Ingenting publicerat.

Eftergranskning mot referensen: nio luftigare synliga rader, KPI-ikoner centrerade vertikalt, positiva bruttovinstbelopp i normal textfärg och färg endast för negativa belopp. Den exakta SVG-formeln verifierad i tillfälliga DAX-frågor för positiv, negativ, tom och extrem marginal. Befintliga sex filterkontexter matchar fortfarande CSV-underlaget. Nya skärmbilder öppnade och granskade efter varje korrigeringsomgång.


Datumkontroll: Transaktioner använder nu ett kompakt inbyggt datumintervall med två datumfält och kalenderikoner enligt referensen, utan skjutreglage. Månad/År ersätts endast på denna sida. Start- och slutdatum samt filter är 2025-01-01–2025-12-31. PBIR validerad och senaste omladdade sidan visuellt granskad; native datumfält har en tunn kantlinje. Ingen ny klickkontroll av datumval utfördes i denna korrigering.
