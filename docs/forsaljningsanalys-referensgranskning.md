# Försäljningsanalys – referens och granskning

Referensen visar fem lika stora KPI-kort med huvudvärde och rundad förändringsetikett, utan sparklines. Under dem finns ett brett kombinationsdiagram till vänster och en hög säljarlista till höger. Vänsterkolumnens nedre kort innehåller en fyraradig marknadstabell och fyra små omsättningstrender med dropdown. Säljarlistan visar sju profiler med avatar, namn, segmenterad indikator, belopp och årsförändring. Högerkortets nederkant linjerar med den nedre marknadsdelen.

Anpassningar: Aubecos färger, svenska och befintliga data; initialer i avatarer enligt Ledningsöversikten. Dropdownen grupperar trender efter Land eller Kategori; referensen visar bara Land utan hela alternativlistan. Kategorien använder befintliga tre grupper Elektronik, Hem och kök och Övrigt; inga produkter utesluts. Ingen dekorativ drillthrough-pil eller specialdesignad tooltip-sida skapas.

Arbetsordning: rubrik/filter, fem KPI-kort, kombinationsdiagram, marknadstabell, marknadstrender, säljarlista och helhetskontroll. Varje del jämförs med referensen, sedan granskas hela sidan med helår och en vald månad. Filterdefinitioner och datamått kontrolleras separat från faktiska klicktester.

Sidbyggaren skriver bara Försäljningsanalys. Övriga sidor och befintliga gemensamma komponenter bevaras. Datan genereras inte om och realistiska produktnamn behålls. Kompletterande mått har prefix Säljanalys och ligger dolda i Försäljningsanalys/Presentation.

Slutkontroll: varje del har granskats i nya, fullt renderade Desktop-bilder. KPI-raden saknar sparklines; marknadstabellen saknar scrollister och visar färgade förändringar samt andelsindikatorer; säljarlistan har sju dynamiskt rangordnade profiler med initialer. Huvuddiagrammet använder en svensk månadsaxel, separata värdeaxlar och dynamisk betoning av högsta månadsomsättning. Kvartalsmarkeringarna visas i helårsvyn. Kortens underkanter linjerar.

Helår 2025, oktober och september–oktober har kontrollerats genom explicita filterdefinitioner och aktuell Desktop-bildgranskning. Land och Kategori har granskats, inklusive tre kategorier och tom fjärde rad. Klickautomationen kunde inte bekräfta dropdownvalet och månadsklicket; dessa redovisas därför inte som godkända klicktester.

Oberoende CSV-kontroll mot aktuella DAX-resultat godkänner tre perioders KPI-värden, 21 säljarplaceringar, 84 månads-/gruppvärden och samtliga min-/maxmarkörer. Tom filterkontext ger tomma värden utan beräkningsfel. Alla datakällors SHA256 matchar befintlig manifestfil; 30 realistiska produktnamn är bevarade. PBIR-kontrollen rapporterar inga fel men varnar för att Desktop-schemat 2.13.0 inte kan hämtas. TMDL har validerats med Microsoft TOM: nio Import-tabeller och fyra enkelriktade relationer.

Teknisk anpassning: Power BI visar en platshållare när vanliga linjediagram görs så låga som referensens minitrender. Dessa återges därför som måttstyrda SVG-bilder i inbyggda tabellvisualer, med ytfyllnad och gröna/röda extrempunkter. De följer period och gruppering, men har ingen separat punktvis hovring. Avataren använder initialer eftersom befintliga porträtt saknas. Ingenting publiceras.

Efterkontroll: textstorlekarna matchar Ledningsöversikten (KPI-rubrik 15 pt, förändring 10 pt, diagrametiketter 9 pt, säljarnamn 12 pt och säljarförändring 9 pt). Minitrenderna skalar nu den valda periodens första och sista månad över hela bildbredden; en månad visas som en centrerad punkt. SVG-bildens proportioner matchar visningsytan. Andelsvärdena har större text och bildhöjd. Nya Desktop-bilder har granskats för januari–mars och helår. DAX-/SVG-kontroll godkänner antal punkter, full bredd och koordinatgränser för helår, januari–mars och oktober i båda grupperingarna.
