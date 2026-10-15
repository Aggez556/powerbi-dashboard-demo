# Uppdrag / beläggning

Sidan finns i **befintliga Ledningsrapport.pbip**, i samma rapport och modell som Ledningsöversikt, Försäljningsöversikt, Kunder och Budget. Ingen separat projektvariant skapades. Startkortet och sidonavigationen länkar till sidan. Den befintliga Aubeco-sidebaren är bevarad. En dold, inbyggd Power BI-tooltipsida visar kapacitetsdetaljer.

## Två tidsfönster

Historiken använder rapportens befintliga R12/Helår/Månad-väljare och samma Periodstart/Periodslut. Standard är R12 oktober 2025–september 2026. Endast historiska slutperioder med jämförelseunderlag visas. Månadsläget visar den valda månaden i KPI-korten och tolv månader historisk kontext i trenddiagrammet, med den valda månaden markerad.

Planläget hämtas från `data/Planinställning.csv`: 30 september 2026. Planveckorna är alltid v41–48, 5 oktober–29 november 2026. Planfakta har **ingen relation till historikens Datum eller Trendaxel**. Planmåtten tar bort enbart historiska datum-/periodfilter och behåller område, resursgrupp och medarbetare. Diagraminteraktion från historisk trend till planvisualer är avstängd.

Område omfattar endast Teknisk service och Bemanning. Resursgrupper som inte finns inom aktuellt område filtreras bort ur väljaren. Om ett gammalt gruppval kvarstår efter ett områdesbyte används alla grupper i det nya området; den synliga urvalstexten anger denna återgång. Historik och plan använder samma effektiva resursurval.

## Data och definitioner

- Det befintliga Uppdrag.csv ger unika avslutade uppdrag och slutförandedatum. Avbokade rader räknas inte. Dess befintliga timmar och exempeluppdragens hela timmar bevaras. Saknad tid på generiska löpande uppdrag kompletteras reproducerbart med godkända, debiterbara tidrapporter på arbetsdagar. Månadsprofilerna för service och bemanning är uttryckliga demoantaganden, inte importerade verkliga observationer. Utförandedatum genereras från arbetskalendern oberoende av fakturadatum. Kontrollfilerna `Utförd tid komplettering.csv` och `Tidrapporteringsprofiler.csv` gör kompletteringen spårbar. Kompletterade timmar ryms inom personens återstående dagskapacitet. Befintligt faktiskt underlag kapas inte om det överstiger en demoprofil.
- Varje uppdrag har en ansvarig resurs i demon. Resursfilter når därmed både tid och uppdragsekonomi utan att duplicera hela intäkten per person. Resurserna är nya operativa dimensioner eftersom medarbetarregister saknades.
- Intäkts- och kundfördelade kostnadsrader från befintliga ekonomiska fakta tilldelas exakt en leverans för samma kund/område/månad, eller ett löpande kunduppdrag. Det är en dokumenterad reproducerbar demofördelning, inte nya ekonomiska belopp. Kalkylmarginal i historiskt KPI vägs med samma periodintäkter.
- Direkta kostnader som saknar kund-/uppdragskoppling fördelas **inte** på påhittade uppdrag. De ligger kvar i den gemensamma områdesekonomin. Kontrollfilen `Ej uppdragsfördelade kostnader.csv` avstämmer dem mot ursprungskällan; uppdragsfördelad kostnad plus denna rest stämmer exakt med området. Uppdragsmarginal och områdesmarginal har därför olika kostnadsomfattning.
- Arbetskapacitet har en unik rad per medarbetare och arbetsdag: schema minus svensk helgdag/fastställd demoledighet. Administration ligger kvar i nämnaren. Debiteringsmål är 82 % för samtliga grupper.
- Planen innehåller individuell kapacitet och bokningar på samma person/dag. Ledigt och överbokat räknas före summering. Planens fasta veckor har ingen ytterligare frånvaro. Bokningar över 100 % kapas inte; noll kapacitet med bokningar visas som saknad kapacitet med varningssignal.
- Uppdragstabellen väljer aktiva intervall som överlappar historisk period. Planerade timmar, utfört hittills och slutprognos gäller hela uppdraget, inte bara vald period. Status är aktuell dataversion, inte historisk snapshot.
- Riskregel: endast pågående uppdrag, utförda timmar över kalkyl eller slutprognos minst två procentenheter under kalkyl. Avslutade uppdrag visar faktiskt slututfall. Klick på en uppdragsrad visar ansvarig, intäkter, direkta kostnader och återstående kostnadsbedömning i detaljraden under tabellen. Tabellen har ingen generisk totalrad och kan skrolla genom samtliga matchande uppdrag.

## Kontroller och avvikelser mot bilden

Faktisk DAX i Power BI Desktop har kontrollerats för 12 kombinationer av period/område/grupp, 32 grupp/veckoceller, 240 medarbetar/veckoceller, alla 3 436 uppdrag samt de fyra statusfiltren. I standardläget matchar 1 243 uppdrag periodens aktiva intervall; 960 är avslutade och 283 pågående. Tolv månaders historisk kontext och exakt en vald-månad-markering har verifierats.

Planen ger exakt 6 800 / 8 000 = 85 %, 1 280 lediga och 80 överbelagda timmar. Värdena är oförändrade vid Helår 2025, Helår 2024, Månad september 2026 och pålagd historisk datumfiltrering. Nord har 110 % under v41–44 och 90 % under v45–48; Syd 90/80 %, Diskpersonal 85,714 % och Städpersonal 72 %.

Det första tidsunderlaget saknade merparten av löpande uppdrags tid och gav därför en missvisande låg debiteringsgrad. Efter kompletteringen ger källdatat **Helår 2025: 38 461,60 / 48 400 h = 79,5 %** och **R12 september 2026: 39 645,98 / 48 600 h = 81,6 %**. KPI och trend beräknas fortfarande från samma faktiska tidrader och kalenderkapacitet; månadsprofilerna används endast av datageneratorn. Generiska fleråriga uppdrags totala tidskalkyl kompletteras också så att gamla 240-timmarsplatshållare inte felaktigt flaggar varje ny tidrapport som överskridande. Exempeluppdragens kalkyler är bevarade.

Bildens 38 400 h och 80 % används inte som hårdkodade KPI-värden. Uppdragsmarginalen baseras på faktiska fördelade kostnader och kan avvika från bildens 22,5 %. Gemensam ekonomi är oförändrad: R12 omsättning 139,50 Mkr, bruttovinst 36,04 Mkr, EBIT 8,00 Mkr, 270 aktiva kunder och 960 avslutade uppdrag (640 teknisk service, 320 bemanning), mot 840 föregående period.

Budgetens Excelkontroller, 191 gamla mått, 44 budgetmått och tre budgetpresentationsmått är bevarade. Budget har fortsatt inget områdesfilter.

Sidans senaste formatering ger en bredare beläggningsmatris med centrerade procentsatser, färgmarkörer i legenden och enhetliga diagramrubriker. Uppdragstabellen visar en tydlig riskkolumn, högerställda numeriska värden och streck när prognos saknas. En saknad prognos räknas inte som noll marginal; tidsöverskridanden kan fortfarande flaggas även utan prognos. Statusordningen lagras i en separat importerad nyckel: Alla, Pågående, Avslutade, Behöver uppföljning. En extra presentationsåtgärd `Uppdrag prognostext` är tillagd; grundmåttets numeriska prognos är bevarad. `scripts/polish-assignment-page.cjs` och `scripts/polish-assignment-model.py` återanvänder befintliga identiteter och periodval.

DAX- och datakontroller är inte UI-test. Automatisk Desktop-rendering har tidigare blockerats av rapportverktygets anslutning/startproblem; ny screenshotgranskning ska redovisas separat när den fungerar.

## Reproducera

1. `python scripts/generate-assignment-data.py` kompletterar demodata utan att ändra gamla faktakällor.
2. `python scripts/build-assignment-model.py` skriver de 11 operativa tabellerna, 58 måtten och åtta enkelriktade relationer. Kör modellgeneratorn inför första import; efter Desktop-sparning ska metadataändringar göras med hänsyn till befintliga lineage-taggar.
3. `node scripts/build-assignment-page.cjs` bygger sidan och aktiverar navigationen i originalrapporten.
4. Öppna Ledningsrapport.pbip och uppdatera data. `scripts/prepare-assignment-check.py` förbereder DAX-kontrollen; `scripts/load-budget-model.ps1 -QueryOnly` används med respektive assignment-frågefil för skrivskyddad verifiering.
5. `python scripts/verify-assignment.py` jämför faktiska DAX-resultat med CSV-källorna. Resultat finns i `validation/assignment-verification.json`.
6. `python scripts/check-assignment-timesheets.py` kontrollerar kompletterade timmar, arbetsdagar, personkapacitet och bevarade avslutade uppdrags timmar. Resultat finns i `validation/assignment-timesheet-check.json`. Kör `scripts/refresh-assignment-model.ps1 -TimeOnly` för att enbart uppdatera tidrapportering och uppdragskalkyler i en redan öppnad modell. Om den automatiska uppdateringen får timeout krävs uppdatering i Desktop; kalla inte CSV-kontrollen för genomförd DAX- eller UI-verifiering.

Inget har publicerats eller pushats till GitHub som del av detta bygge.
