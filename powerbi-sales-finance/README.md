# Aubeco Sales & Finance

Ett separat lokalt Power BI-projekt med startsida och Ledningsöversikt enligt de två bifogade referenserna, anpassat till Aubecos färger, ordmärke och svenska talformat. Projektet påverkar inte det tidigare AubecoHandel-projektet. Inget publiceras.

Öppna **AubecoSalesFinance.pbip** i en aktuell Power BI Desktop och välj **Start → Uppdatera** för att läsa de nio lokala Import-tabellerna. Om projektet flyttas, ändra parametern DataFolder i Transformera data → Hantera parametrar till den nya absoluta data-mappens sökväg.

Startsidan har fyra kort med sidnavigation. Alla fyra undersidor är byggda: Ledningsöversikt, Ekonomi och lönsamhet, Försäljningsanalys och Transaktioner. I Desktops redigeringsläge används **Ctrl+klick** för navigationsknappar.

Ledningsöversikt har omsättning, sålda enheter, bruttovinst, bruttomarginal och leveranser, med årsjämförelse och minitrender. Diagrammen visar månad, land eller kategori, säljteam, tre största säljare och fem största produkter. Dropdown-valen ändrar trendmått, land/kategori och produktmått. De är inbyggda Power BI-slicers, inte dekorativa knappar. Årsvalet är 2025 från början; 2024 saknar föregående års data.

Alla uppgifter är fiktiva: 10 000 orderrader, 4 000 order, 100 kunder, 30 produkter i fem kategorier, 24 säljare i tre team, fyra länder och 731 kalenderdatum för 2024–2025. En order räknas som en leverans. SEK exklusive moms. Fast seed 20261007 gör datan reproducerbar. Bildens exakta personer, produktnamn och belopp har inte kopierats.

Modellen är en stjärnmodell med fyra aktiva, enkelriktade många-till-en-relationer och fyra fristående väljartabeller. Datum är markerad, nycklar är dolda. Marginal- och koncentrationsförändring uttrycks i procentenheter (pp), övriga förändringar i procent. Aubecos ordmärke är inbäddat lokalt som PNG och behöver inget installerat webbtypsnitt.

Ekonomi och lönsamhet visar bruttovinst, marginal, varukostnad och omsättning/vinst per enhet med årsjämförelser och månadstrender. En väljare växlar månadsdiagrammets små multiplar mellan säljteam och kategori. Fem produkter rankas efter bruttovinst. Landsvyerna visar vinst, årsförändring och marginal, med andel i verktygstips. Spridningsdiagrammet jämför varje produkts varukostnad och bruttovinst; kategorin styr färgen.

Försäljningsanalys visar aktiva säljare, omsättning per säljare, leveranser, genomsnittlig order och de fem största säljarnas omsättningsandel. Topp 5-andelen beräknas om i aktuellt filterurval. Säljarlistan visar topp 10 med årsförändring, bruttovinst, marginal och leveranser i verktygstips. Landstabellen och små multiplar visar marknadernas omsättning och utveckling. Månadstrenden jämför omsättning och bruttovinst.

Transaktioner visar omsättning, antal enheter, bruttovinst, marginal och leveranser för valt datumintervall och produkturval. Datumintervallet täcker från början båda dataåren. Skriv en produkt eller del av ett produktnamn i det inbyggda textfiltret och tillämpa sökningen. Tabellens radnummer förhindrar att likadana orderrader slås ihop; ordernummer gör order spårbara. Tabellen visar datum, säljare, team, land, kategori, produkt, enhetspris, antal, varukostnad, omsättning, bruttovinst och marginal. Pengar visas med ören, antal är heltal. Power BI ger automatiskt vertikal rullning för de 10 000 raderna och horisontell rullning när kolumnerna inte ryms. Marginalceller använder en diskret färgskala som alternativ till referensens specialbyggda datastaplar. Export följer befintlig rapportinställning för sammanfattade data.

Referensbildernas porträtt och dekorativa kontroller har anpassats till inbyggda, interaktiva visualiseringar. Säljarna är fiktiva och inga foton används. Bruttovinst betyder omsättning minus varukostnad; rörelsekostnader, skatt och frakt ingår inte. Genomsnittlig order är omsättning per unik order, inte per orderrad. Aktiva säljare har minst en orderrad i urvalet. Första dataåret saknar jämförelsedata från föregående år.

Återskapa från projektroten, med detta projekt stängt i Desktop:

```powershell
python scripts/generate-sales-finance.py
node scripts/build-sales-finance.cjs
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/validate-sales-finance.ps1
python scripts/verify-sales-finance.py
& ./.tools/powerbi/node_modules/.bin/powerbi-report-author.cmd --out powerbi-sales-finance/validation/pbir-result.json validate powerbi-sales-finance/AubecoSalesFinance.pbip
```

Generatorerna skriver över detta projekts data, modell och visualfiler. Befintlig scaffold behövs för rapportens grundfiler. Valideringsresultat sparas i validation. TMDL- och schemavalidering skiljs från faktisk Desktop-inläsning, exekverad DAX och skärmbildsgranskning.
