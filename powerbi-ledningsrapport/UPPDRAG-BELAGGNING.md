# Uppdrag / beläggning

Sidan finns i **befintliga Ledningsrapport.pbip**, i samma rapport och modell som Ledningsöversikt, Försäljningsöversikt, Kunder och Budget. Ingen separat projektvariant skapades. Startkortet och sidonavigationen länkar till sidan. Den befintliga Aubeco-sidebaren är bevarad. En dold, inbyggd Power BI-tooltipsida visar kapacitetsdetaljer.

## Två tidsfönster

Historiken använder rapportens befintliga R12/Helår/Månad-väljare och samma Periodstart/Periodslut. Standard är R12 oktober 2025–september 2026. Endast historiska slutperioder med jämförelseunderlag visas. Månadsläget visar den valda månaden i KPI-korten och tolv månader historisk kontext i trenddiagrammet, med den valda månaden markerad.

Planläget hämtas från `data/Planinställning.csv`: 30 september 2026. Planveckorna är alltid v41–48, 5 oktober–29 november 2026. Planfakta har **ingen relation till historikens Datum eller Trendaxel**. Planmåtten tar bort enbart historiska datum-/periodfilter och behåller område, resursgrupp och medarbetare. Diagraminteraktion från historisk trend till planvisualer är avstängd.

Område omfattar endast Teknisk service och Bemanning. Resursgrupper som inte finns inom aktuellt område filtreras bort ur väljaren. Om ett gammalt gruppval kvarstår efter ett områdesbyte används alla grupper i det nya området; den synliga urvalstexten anger denna återgång. Historik och plan använder samma effektiva resursurval.

## Data och definitioner

- Det befintliga Uppdrag.csv ger unika avslutade uppdrag och slutförandedatum. Avbokade rader räknas inte. Dess befintliga timmar återanvänds som reproducerbart tidsunderlag, kompletterat med spårbara pågående exempeluppdrag. Detta är ett antagande om godkänd, debiterbar utförd tid i demon; verkliga tidrapporter saknades tidigare.
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

Historiska timmar är **15 348 h**, kapacitet **48 600 h**, alltså cirka **31,6 %** debiteringsgrad. Bildens 38 400 h och 80 % används inte som hårdkodade KPI-värden. Skillnaden följer av att det tidigare uppdragsunderlaget innehöll färre timmar. Uppdragsmarginalen baseras på faktiska fördelade kostnader och kan avvika från bildens 22,5 %. Gemensam ekonomi är oförändrad: R12 omsättning 139,50 Mkr, bruttovinst 36,04 Mkr, EBIT 8,00 Mkr, 270 aktiva kunder och 960 avslutade uppdrag (640 teknisk service, 320 bemanning), mot 840 föregående period.

Budgetens Excelkontroller, 191 gamla mått, 44 budgetmått och tre budgetpresentationsmått är bevarade. Budget har fortsatt inget områdesfilter.

DAX- och datakontroller är inte UI-test. Automatisk Desktop-rendering har tidigare blockerats av rapportverktygets anslutning/startproblem; ny screenshotgranskning ska redovisas separat när den fungerar.

## Reproducera

1. `python scripts/generate-assignment-data.py` kompletterar demodata utan att ändra gamla faktakällor.
2. `python scripts/build-assignment-model.py` skriver de 11 operativa tabellerna, 58 måtten och åtta enkelriktade relationer. Kör modellgeneratorn inför första import; efter Desktop-sparning ska metadataändringar göras med hänsyn till befintliga lineage-taggar.
3. `node scripts/build-assignment-page.cjs` bygger sidan och aktiverar navigationen i originalrapporten.
4. Öppna Ledningsrapport.pbip och uppdatera data. `scripts/prepare-assignment-check.py` förbereder DAX-kontrollen; `scripts/load-budget-model.ps1 -QueryOnly` används med respektive assignment-frågefil för skrivskyddad verifiering.
5. `python scripts/verify-assignment.py` jämför faktiska DAX-resultat med CSV-källorna. Resultat finns i `validation/assignment-verification.json`.

Inget har publicerats eller pushats till GitHub som del av detta bygge.
