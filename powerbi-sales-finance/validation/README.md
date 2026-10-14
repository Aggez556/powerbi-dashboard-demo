# Kontrollstatus

## Transaktionssidan

Den sista undersidan är byggd med fem KPI-kort, datumintervall, inbyggt produktsök och scrollbar tabell. Radnyckeln är med i tabellens gruppering, vilket bevarar orderradens detaljnivå. Totalsummeringen är avstängd; KPI-korten visar urvalets totaler. Inga modell-, mått- eller dataändringar behövdes. PBIP/PBIR har 0 fel och 0 varningar. En läsande DAX-fråga i den redan öppna modellen verifierade fem riktiga transaktionsrader mot oberoende CSV-joins och Decimal-aritmetik: datum, rad/order, säljare, team, land, kategori, produkt, enhetspris, antal, kostnad, omsättning, vinst och marginal stämmer. Se desktop-transactions.json och transaction-comparison.json. Detta verifierar data och mått i den befintliga Desktop-modellen; senaste PBIR är ännu inte visuellt granskad eftersom Desktop rapporterar osparade ändringar. Äldre noteringar om platshållare gäller tidigare versioner.

## Nya undersidor

Ekonomi och lönsamhet samt Försäljningsanalys är byggda med inbyggda KPI-kort, diagram, tabeller, små multiplar och årsfilter. Transaktioner är den enda kvarvarande platshållaren. Modellen har nu nio Import-tabeller: Finansaxel ger ett val mellan säljteam och kategori utan att ändra försäljningsdatan. Fyra enkelriktade relationer är bevarade. 27 analysmått har tillkommit.

PBIP/PBIR: **0 fel och 0 varningar**. TOM läser den nya TMDL-modellen. CSV-aritmetik verifierar även aktiva säljare, genomsnittlig order, vinst/omsättning per enhet, omsättning per säljare och de fem största säljarnas andel. Faktisk DAX-körning och skärmbildsgranskning av de två nya sidorna återstår tills senaste TMDL/PBIR är laddade i Desktop. Äldre kontrollanteckningar nedan gäller tidigare versioner.

## Senaste ändringar – förenklade rubriker och diagramfilter

Senaste PBIP/PBIR-valideringen visar **0 fel och 0 varningar**. Startsidan har en enda huvudrubrik, Försäljning och ekonomi; Verksamhetsanalys och den upprepade mindre rubriken är borttagna. Rapportens verifierade schemaegenskap settings.locale är sv-SE. KPI-värden är vänsterjusterade med extra inre ramar och bakgrunder avstängda. Månads-, marknads- och produktdiagram har en egen rubrikrad med filter ovanför diagramytan. Legender använder Aktuellt år och Föregående år.

**Slutlig visuell kontroll av dessa ändringar väntar på manuell omöppning**, eftersom Desktop rapporterar osparade ändringar. Stäng AubecoSalesFinance utan att spara den äldre Desktop-versionen, öppna projektfilen igen och välj Uppdatera. Äldre kontrollanteckningar nedan beskriver föregående versioner.

PBIP/PBIR har validerats mot officiella scheman med Power BI Report Author CLI: **0 fel, 0 varningar**. Microsoft TOM kan läsa TMDL: åtta Import-tabeller och fyra aktiva, enkelriktade många-till-en-relationer.

CSV-kontrollen granskar alla radantal och filhashar, hela kalendern, unika primärnycklar, främmande nycklar, orderkonsistens, radbelopp och positiva marginaler. Den beräknar årsresultaten oberoende med Decimal. Rapportens fältbindningar, sidnavigation och canvasgränser kontrolleras också.

Det nya projektet öppnades i en separat Desktop-instans. Full Import-refresh via dess lokala Analysis Services-motor lyckades. DAX för båda åren jämfördes med CSV och stämde för alla 13 fält. Resultatet före sista justeringen finns i desktop-dax-before-final-fix.json. Sista justeringen gör marginalförändringen tom när föregående år saknas; den behöver verifieras i den senaste Desktop-versionen.

För 2025 är omsättningen 15 374 362,60 kr, bruttovinsten 4 096 778,32 kr, bruttomarginalen 26,65 %, sålda enheter 24 244 och leveranser 2 166. Omsättningens årstillväxt är 16,42 %.

Startsidan granskades i en riktig Desktop-skärmbild. Små rullister i två ikonfält rättades därefter i filerna. Executive Overview-skärmbilden visade laddningsindikatorer, vilket innebär att diagrammens rendering ännu inte är godkänd. Tre platshållarsidor är filvaliderade men inte skärmbildsgranskade. Senaste filer kräver manuell omöppning eftersom Desktop rapporterar osparade ändringar. Tillfälliga skärmbilder sparas inte i projektet.

Stäng det nya projektet utan att spara den äldre Desktop-versionen. Öppna AubecoSalesFinance.pbip igen och välj Start → Uppdatera. Den befintliga AubecoHandel-rapporten behöver inte stängas.

## Svenska och layoutjusteringar

Rapportens sidnamn, rubriker och navigationsknappar har översatts till svenska. Årsjämförelse visas som Årsförändring. Fyra lika breda startsideskort, centrerade SVG-ikoner och knappar med korrigerade innermarginaler. Sid-ID och navigation är bevarade. Modellen och datan har inte ändrats i detta steg. PBIR-validering har inga fel; en tillfällig schemahämtningsvarning gäller den oförändrade PBIP-startfilen. Senaste rapportlayouten har lästs in i Desktop. Skärmbildsgranskning pågår.
