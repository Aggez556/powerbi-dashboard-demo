# Felorsak och rättning

Den lokala Desktop-motorn rapporterade syntaxfel i tre budgetmått. DAX-variablerna Helår, Månader, Jämnt, Årsbelopp och Intäkt innehöll tecken som inte tillåts i variabelidentifierare. Version var dessutom ett reserverat namn. Svenska tabell-, kolumn- och måttnamn behålls; variablerna har ersatts med giltiga engelska namn.

Felet var i de skapade DAX-uttrycken. TMDL-deserialisering och PBIR-schema hade passerat, men dessa kontroller kompilerar inte måtten. De faktiska motorfelen lästes via Microsoft TOM från den öppna lokala Desktop-modellen. Alla sex budgetmåtts uttryck uppdaterades där, följt av Calculate. Inga relationer lades till och inga andra mått ändrades. Ingen publicering gjordes.

Matrisens faktiska DAX-fråga kördes därefter med ADOMD mot den befintliga Desktop-motorn. budget-dax-result.json innehåller resultaten, budget-dax-checks.json jämför dem med oberoende CSV/SQL-värden och budget-live-fix.json innehåller måttens motorstatus. Sparade uttryck före rättning finns i budget-measures-before-fix.json.

Procentreglagets numeriska start har också satts till 3 och Bas/Justerad-korten har mindre text och mindre intern padding i PBIR-filerna. Dessa utseendeändringar måste laddas in manuellt om Desktop har osparade ändringar. För att bevara dem, spara eventuella egna ändringar separat och öppna den uppdaterade projektfilen; skriv inte den tidigare öppna rapportlayouten över de korrigerade filerna.

Ett godkänt DAX-resultat bevisar beräkningarna, inte att Desktop visar den senaste PBIR-layouten. Visuell granskning av den nya layouten återstår.
