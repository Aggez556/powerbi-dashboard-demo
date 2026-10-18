# Försäljning per bransch

Kundsidans nedre vänstra kort visar förändringen i nettoförsäljning mot samma månad föregående år. Sidans periodval styr vilka månader som visas: R12 ger tolv månadsjämförelser, Helår kalenderårets månader och Månad en enda månadsjämförelse. Varje punkt är månadsvis årsförändring, inte ett nytt R12-värde.

- Procent är standard: fem tunna linjer med diskreta punkter.
- Kronor visar grupperade staplar; axeln använder Mkr och hovring visar exakta kronor.
- Båda skalorna anpassar övre och nedre gränsen separat till synliga månader och valda branscher. Noll ingår alltid, med 8 % luft runt värdena och avrundning i steg om 5 procentenheter respektive 0,1 Mkr.
- Färgerna är fasta mellan vyerna: restaurang marinblå, hotell grön, catering blå, kontor ockra och livsmedel blågrå.
- Diagrammets legend följer branschurvalet. Det finns inga permanenta sifferetiketter på linjer eller staplar.
- Procent visas endast när motsvarande månads försäljning föregående år är positiv. Nollreferens eller saknat jämförelseunderlag ger inget procentvärde. Kronförändringen kan fortfarande visas.
- Bokmärkena växlar bara diagram och knappar. De sparar inte period-, bransch- eller andra dataval och är separata från växlingen i kortet ovanför.

Nio mått har lagts till i Kunder. Faktadata, relationer och partitionstyper är oförändrade. Kör `build-industry-change-model.py` för modellkällan och `build-industry-change-card.cjs` för rapportkortet. `apply-industry-change-model.ps1` uppdaterar mått i en öppen originalmodell utan dataimport.

Verifiering: `check-industry-change-data.py` jämför fakturarader med faktiska DAX-resultat för 221 månads-/branschkombinationer över sex period-/branschurval. Referensen använder den importerade kundmodellens branschindelning, eftersom den befintliga importcachen skiljer sig från Kunder.csv. Denna uppgift ändrar inte den befintliga kundindelningen. Framtida full datauppdatering läser filernas branschindelning som vanligt.

Strukturkontrollen `check-industry-change-card.cjs` kontrollerar axelbindningar, båda växlingsriktningarna och separata bokmärken. Visuell granskning och klicktest i Desktop är en separat kontroll.
