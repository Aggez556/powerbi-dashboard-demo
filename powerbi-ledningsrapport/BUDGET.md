# Budget – Excel-scenarier och gemensamt utfall

Öppna `Ledningsrapport.pbip` i Power BI Desktop och välj **Uppdatera**. Den nya sidan heter **Budget**. Startkortet och sidomenyn länkar till den. Ingen publicering eller webbversion ingår.

## Ändra budgeten

1. Öppna [data/Budgetscenarier.xlsx](data/Budgetscenarier.xlsx).
2. Välj års-/scenarioflik. Ändra de blå beloppscellerna: kronor, intäkter positiva och kostnader negativa. Behåll KontoID, ScenarioID, kolumnrubriker och Excel-tabellerna.
3. Spara och stäng arbetsboken. Välj **Uppdatera** i Power BI Desktop.

Power Query läser arbetsbokens strukturerade tabeller direkt via `Excel.Workbook`. Månaderna avpivotteras till Månadsnyckel, KontoID, ScenarioID och Belopp. Inga Excel-summor importeras och inga Excel-formler behöver räknas om. Sökvägen konfigureras med parametern **BudgetWorkbook**, som normalt följer **DataFolder**.

Kör inte generatorn med `--reset-workbook` på en ändrad budget: det flaggvalet ersätter arbetsboken. Normal körning av `scripts/budget-scenario-data.py` bevarar den befintliga arbetsboken och återskapar bara mappningarna.

## Period och jämförelse

Standard: 2026, Fastställd budget, Scenario mot utfall, juli–september, Månad. Återställ filter återställer dessa val samt matrisens standardexpandering. Övriga rörelsekostnader och IT är expanderade i den sparade standardvyn.

2024 och 2025 innehåller Fastställd budget. Försiktigt och Offensivt finns för samtliga tolv månader 2026. Att välja **Jämför scenarier** väljer därför 2026 och visar jämförelsescenariot. Vid byte till ett historiskt år används alltid Fastställd budget mot utfall. Rubriken visar den effektiva jämförelsen.

Scenario mot utfall använder enbart avslutade månader, senast september 2026. Oktoberutfall finns i det gemensamma källmaterialet men betraktas som ofullständigt på Budget. Jämför scenarier tillåter även oktober–december. Om ett kvarvarande månadsval inte innehåller någon tillåten månad visas streck i stället för en påhittad nollavvikelse.

Månadskolumnerna visar egna belopp. Ackumulerat summerar endast de valda månaderna, i ordning, från urvalets första månad. KPI-kort och Vald period summerar perioden en gång. Marginalerna är kvoter av summerade belopp. Procentavvikelse mot noll eller negativ resultatbas visas som streck; absolut beloppsavvikelse kvarstår.

Scenario mot utfall: Avvikelse = Utfall − Budget. Scenariojämförelse: Avvikelse = A − B. A/B-namn framgår av rubrik och kolumnetiketter. Kostnader är negativa, så lägre kostnader ger grön avvikelse. Marginalavvikelse visas i procentenheter.

## Avstämning och antaganden

Utfallen kommer från de befintliga Försäljning, Direkta kostnader och Gemensamma kostnader. Ingen separat utfallsfaktatabell har skapats. Budgeten får gemensamma månads-/kontonycklar; datumkontext överförs till befintliga fakta via TREATAS. Scenarier, konton och budgetperioder har enkelriktade dimension–fakta-relationer, utan fakta–fakta-relationer.

Den tidigare budgeten hade bara EBIT per månad. Excel-detaljerna är därför en dokumenterad demofördelning: omsättning 95 % av utfall, direkta kostnader 94 % och resterande gemensamma kostnader fördelas proportionellt så att EBIT exakt motsvarar ursprunglig Budget.csv. Den befintliga modelltabellen Budget läser nu samma Excel-scenarios sammanräknade EBIT. En budgetändring slår alltså även igenom i Ledningsöversiktens budget efter uppdatering. Original-CSV ligger kvar som avstämningsunderlag, inte som en andra aktiv budgetkälla.

Gemensamma källkostnader saknar IT-/marknadsföringsdetaljer. Administration fördelas till gemensam personal 60 %, licenser 10 %, IT-drift 6 %, IT-konsulter 4 %, marknadsföring 8 % och administration resterande 12 %. Avrundningsrest läggs på administration. Lokaler och avskrivningar återanvänds separat. Direkt leveranspersonal och ej uppdragsfördelad direkt personal ligger kvar bland direkta kostnader och räknas inte igen bland gemensam personal. EBIT innehåller avskrivningar exakt en gång.

Försiktigt: omsättning −8 %, direkta kostnader −5 %, övriga gemensamma kostnader +2 %. Offensivt: omsättning +10 %, direkta kostnader +6 %, övriga gemensamma kostnader +3 %. Avskrivningar är oförändrade. November/december 2026 bygger på motsvarande månader 2025 med 10 % tillväxt. Beloppen är sparade i Excel och styrs inte av reglage i rapporten.

### Skillnad mot referensbilden

Gemensamma utfall har bevarats. Juli–september 2026 är därför omsättning **44,760923 Mkr**, bruttovinst **11,383446 Mkr**, EBIT **1,733574 Mkr** och bruttomarginal **25,4317 %**. Fastställd budget för samma period är omsättning **42,522878 Mkr**, bruttovinst **11,148050 Mkr**, EBIT **3,128451 Mkr** och bruttomarginal **26,2166 %**. Bildens 42,60/2,70/25,1 % är inte rapportens gemensamma faktiska kontrollcase.

R12 oktober 2025–september 2026 kvarstår: omsättning 139,50 Mkr, bruttovinst 36,04 Mkr, EBIT 8,00 Mkr, budget-EBIT 9,75 Mkr. Inga belopp har femdubblats igen.

## Verifiering

- `scripts/check-budget-tmdl.ps1`: Microsoft TOM läser 38 tabeller och 21 relationer; de 191 tidigare måtten är kvar och 44 budgetmått har tillkommit.
- `scripts/verify-budget-scenarios.py`: 46 månadsvisa avstämningar av Fastställd budget, historiska år, tre scenarier, en/flera/icke sammanhängande månader, ackumulerade perioder, sex A/B-par, kostnadsmappning, oförändrade källfiler, sidgränser, native matris och bokmärkeskonfiguration.
- Excel-ändring har lästs tillbaka och kontrollerats i en oberoende Python-kontroll, därefter har exakt originalfil återställts. Detta är **inte** en verifierad Power BI-datauppdatering.
- `validation/budget-checks.json` innehåller kontrollfallen och anger separat status för faktisk DAX, Excel-refresh, UI-interaktioner och skärmbilder. En godkänd filkontroll innebär inte att dessa UI-steg är verifierade.

Vid första öppningen behöver Desktop importera de nya Excel- och dimensionstabellerna. Ingen publicering krävs. Testa standardläge, Jämför scenarier, Expandera alla/Fäll ihop och Återställ filter i Desktop innan rapporten används som ekonomiskt underlag.



### Uppföljande Desktop-DAX-kontroll

Faktisk DAX har nu körts mot den inlästa budgetmodellen: standardvyn ger 81 ifyllda matrisceller, ett ackumulerat urval ger 81 celler och KPI-/R12-totalerna stämmer. Se validation/budget-live-verification.json. Matrisens kolumnnivå Budget/Utfall behöver vara aktiv tillsammans med månadsnivån; generatorn anger nu detta uttryckligen. Visuell granskning efter denna korrigering och ett faktiskt Excel-refresh-test är fortfarande inte verifierade.


### Sammanh?ngande resultatr?kning

Resultatr?kningen visas som en enda interaktiv Power BI-visual med Deneb 2.0 (MIT-licens). Paketet och licensen ligger i rapportens CustomVisuals-mapp. Det ?r ingen frist?ende webbapp, bild eller ers?ttning f?r rapporten. Excel, DAX, scenarioval och ?vriga Power BI-visualiseringar finns kvar i originalprojektet.

Tabellen har samma ekonomiska radordning som tidigare, med rubrikavsnitt, indrag och bl? summeringsrader. Endast kontogrupper med verkliga underposter f?r klickpilar. Resultat, marginaler och kontoblad saknar pilar. ?vriga r?relsekostnader och IT ?r ?ppna i startvyn. Expandera alla och F?ll ihop ?r nu direkta kontroller inne i tabellen. Huvuden och radetiketter ligger fast medan beloppen skrollas p? en gemensam yta.

Budgetrapportnoder ?r en frist?ende presentationstabell med 26 noder och inga finansiella belopp. Tre nya m?tt ?teranv?nder de befintliga RR-m?tten och scenariokolumnerna. ?ndra budgetbelopp i samma Excel-arbetsbok som tidigare. Deneb beh?ver ingen separat betald visuallicens. Visualen anv?nder inga externa dataadresser.

?ppna Ledningsrapport.pbip och v?lj Uppdatera f?rsta g?ngen f?r att l?sa den nya presentationstabellen. Ingen ny projektfil kr?vs. Vega-definitionen ?r redigerbar i Denebs editor och sparas ?ven i validation/budget-statement-spec.json. ?terskapa komponenten med scripts/install-budget-statement.cjs. Scripts/budget-statement-model.py skapar endast den nya presentationsdimensionen och dess tre m?tt; skriv inte ?ver Desktop-tilldelade lineageTag efter att modellen laddats.

Verifiering: scripts/test-budget-statement.mjs k?r den riktiga Vega-motorn lokalt och testar klicksignal, expandera/f?ll ihop, nio hopf?llda huvudrader, 26 fullt expanderade rader, standardvy med 16 rader, gemensam skroll, enbart riktiga expanderare samt A/B-rubriker f?r tolv budgetm?nader. Underlaget st?mmer med samtliga 81 huvudv?rden fr?n tidigare k?rd Desktop-DAX. Dessa komponenttester ers?tter inte en genomf?rd Power BI-rendering eller en k?rning av de tre nya DAX-m?tten i Desktop. Den slutliga Power BI-granskningen redovisas separat.
# Procentuell budgetavvikelse

Dummybudgetens underkategorier har nu olika konto- och månadsprofiler. Omfördelningen görs inom samma huvudgrupp och scenario, med exakt oförändrad månadssumma. Därför är omsättning, direkta kostnader, bruttovinst, rörelseresultat och marginaler på huvudnivå oförändrade. Utfallsdata ändras inte. Kör Uppdatera i Desktop för att läsa de ändrade Excel-beloppen. Verifiering: validation/budget-detail-variation.json. Äldre live-DAX-kontroller av detaljbelopp avser budgeten före denna omfördelning tills en ny uppdatering och kontroll körts.

Månadsavstånd: budgetdelen använder 88 enheter och utfallsdelen 144 i standardläget. Det minskar varje månads bredd från 288 till 232 (cirka 19 procent), samtidigt som avvikelsen behåller sitt utrymme. Scenariojämförelsens längre rubriker har separat bredd.

Senaste placering: avvikelsen skrivs inom parentes med sex enheters mellanrum direkt efter utfallsbeloppet, exempelvis 9 362 (+5,3 %). Utfallsrubriken är inriktad mot beloppet och månadsbredden är åter kompakt. Ingen separat procentkolumn finns.

Layoutjustering: procentavvikelsen ligger till höger om utfallsbeloppet på samma rad, i mindre färgad text. Utfallscellen reserverar separat utrymme för belopp och avvikelse. Radhöjden är 36 för en kompakt tabell utan två textrader.

Uppdatering: avvikelsen visas nu integrerat under Utfall för varje månad och för Vald period, utan separat avvikelsekolumn. Beloppet behåller sin vanliga färg medan den mindre avvikelseraden visar grönt, rött eller neutralt. Scenariojämförelsen visar motsvarande avvikelse under B. Visualen beräknar indikatorerna från samma bundna månadsbelopp; inga nya modellmått eller kolumnbindningar krävs. Radhöjden har ökats för att hålla de två textraderna åtskilda.

Kolumnen Avvikelse under Vald period visar en färgprick och ett signerat procenttal. Grönt och positivt betyder bättre än budget; rött och negativt betyder sämre. Beräkningen är (utfall − budget) / absolutbeloppet av budget. Eftersom kostnader lagras med negativt tecken blir en lägre kostnad positiv. Marginalrader visar skillnaden i procentenheter (pp). Nollbudget visas som ett neutralt streck; avvikelser som avrundas till noll är grå.

Vid scenariojämförelse används (scenario A − scenario B) / absolutbeloppet av scenario B. Måttet Rapportavvikelse kompletterar de tre befintliga presentationsmåtten; de ursprungliga beloppen påverkas inte. Faktisk Desktop-DAX verifieras i validation/budget-variance-verification.json. Lokala Vega-tester ersätter inte visuell granskning i Desktop.

