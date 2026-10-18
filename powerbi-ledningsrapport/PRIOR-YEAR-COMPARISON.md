# Jämförelse mot föregående års utfall

Välj **Föregående års utfall** under **Jämförelseunderlag** på budgetsidan. KPI-kort och resultaträkning visar aktuellt utfall jämfört med samma valda månader föregående år. Ackumulerad visning summerar inom de valda månaderna. År 2026 begränsas utfallsjämförelser till september, som tidigare.

Referenskolumnen heter **Föregående år**, och KPI-undertexterna anger samma referens. Avvikelser använder samma logik som budgetjämförelsen: positivt betyder bättre utfall, även för negativa kostnader. Marginalskillnader anges i procentenheter. Alternativet använder utfallsjämförelse; scenariejämförelse gäller fortsatt de tre budgetversionerna.

Två dolda mått återanvänder kontomappningen och beräknar föregående års faktiska transaktioner över hela månader. Ingen budget kopieras till föregående år. Budgetscenarion och Budgetkolumner behåller sina ursprungliga M-partitioner med CSV-import. Partitionstypen får inte ändras mot projektets befintliga importcache.

Efter en omgenerering av budgetmodellen: kör `scripts/add-budget-prior-year.py`, därefter `scripts/install-budget-statement.cjs` och den gemensamma formateringspassagen vid behov.

`scripts/check-budget-prior-year.py` genererar 24 oberoende fall över 2024–2026, månadsvis/ackumulerat, sammanhängande/glesa månadsväljningar. Källmodellens föregående-års-uttryck körs under separata frågelokala testnamn mot importerade fakta. Samtliga 144 belopp/marginaler passerade. Kontroll av faktisk väljarladdning och visuell granskning är separata kontroller i Desktop.

Den befintliga Desktop-sessionens filuppdatering fastnade under implementeringen. Stäng den utan att spara den gamla rapportdefinitionen, öppna `Ledningsrapport.pbip` på nytt och välj Uppdatera om Power BI efterfrågar det. Spara efter att den nya layouten och datan har laddats.
