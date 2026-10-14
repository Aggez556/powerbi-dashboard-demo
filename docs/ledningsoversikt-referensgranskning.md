# Ledningsöversikt – återställ referensens struktur

Referens: användarens Executive Overview och detaljbild Revenue by Country i konversationen.

| Del | Tidigare avvikelse | Åtgärd |
|---|---|---|
| Fem KPI-kort | Höga kort, kraftiga mörka sparklines, årlig förändring långt från värdet | Kompakta kort med värde, färgad förändring och diskret ytdiagram |
| Månadsutveckling | Dropdown ersatte toggle | Två valbara knappar: Omsättning / Bruttovinst |
| Marknad | Dropdown; axlar tog plats; etiketter saknades | Land / Kategori-toggle, stapelpar, belopp och årsförändring |
| Säljteam | Stort separat kort, belopp saknades | Gemensam nedre panel med marknad; stapelpar och belopp |
| Säljare | Stort fristående diagram | Kompakt topplista överst i gemensam högerspalt |
| Produkter | Separat kort med dropdown | Topp 5 under säljarlistan; Omsättning / Sålda enheter-toggle |

Aubecos färger och svenska texter behålls. År och Månad behålls enligt användarens senare instruktion. Beloppen kommer från befintlig dummydata, inte från referensbilden.

Inbyggda Power BI-visualiseringar används. Den senaste säljarlistan använder tre separata rundade rader, dynamiska initialer i runda märken och segmenterade staplar. Porträtt saknas för de fiktiva säljarna. De tre toggles är datakopplade knapputsnitt, inte dekorativa bilder. Jämförelse avser motsvarande vald period föregående år.

## Kontroll i Desktop 2026-10-08

| Komponent | Utfall mot referensen |
|---|---|
| KPI-kort | Fem datakort, fullständiga värden, färgad förändring och diskreta ytdiagram. Tidigare diagramikoner är borta. |
| Toggles | Tre datakopplade knappval i sammanhängande kapslar med mörkt aktivt segment. Kompaktare sidutrymme, högerkanten bibehållen, hela texter synliga och ingen scrollbar. Verifierat i Desktop. |
| Månadsdiagram | Aktuellt och föregående år, svenska månadsnamn, läsbar svensk diagramförklaring. Kvartalsgrupperingen i referensen ingår inte. |
| Marknad och team | Stapelpar med belopp och årsförändring; rättade procentformat. Svenska textmått ger mellanrum och enhet, exempelvis `4,03 mn kr`. |
| Säljare | Tabellen är ersatt med tre rundade rader, runda initialmärken, namn överst och segmenterad stapel, belopp samt färgad förändring under. Verifierat i Desktop utan extra vita bakgrunder, avkortade segment eller scrollbars. |
| Produkter | Alla fem produkter synliga, belopp med `mn kr`; etiketten växlar till `st` vid enhetsval. |
| Rubrik och navigation | Befintlig Aubeco-logotyp, svenska rubriker och navigation behålls. År och Månad är senare tillägg jämfört med referensen. |

Rapportens schema är validerat utan fel eller varningar. TMDL har lästs med Microsoft TOM. Den senaste versionen har laddats, beräknats och granskats genom Desktop-skärmbilder. De tillfälliga kontrollbilderna rensas efter granskningen.

Faktisk DAX i Desktop jämfördes med CSV-nycklar och Decimal-summor: samtliga 18 grupper (två år, fyra länder och fem kategorier) överensstämmer. För oktober 2025 gav måttvalen 1 461 932,29 kr i omsättning, 385 622,41 kr i bruttovinst och 2 362 enheter. Dessa kontroller avser modellen och måttvalens filterkontext; manuella klick på varje knapp har inte automatiserats.

Valideringsresultat finns i `powerbi-sales-finance/validation/pbir-result.json`, `overview-comparison.json`, `desktop-overview-labels.json` och `desktop-overview-toggles.json`.

## Senaste korrigering – verifierad i Desktop 2026-10-08

Den transparenta standardfyllningen gjorde även det valda segmentet osynligt i Desktop. Alla segment har nu opak fyllning: det inaktiva matchar den gemensamma kapseln och det aktiva är mörkblått. Månadsdiagrammets förklaring ligger längst ned till höger. Marknad och säljteam har fått 32 enheter högre diagramutrymme för att separera belopp och procent mellan raderna. Säljteamets fasta, dolda skala slutar vid 6,8 mn kr för att ge etiketter utrymme efter staplarna; detta är anpassat till nuvarande dummydata och bör omprövas om datamängden ändras.

Alla tre togglar använder nu automatisk anpassning av två segment till kapselns bredd. Sidutrymmet har minskats med ungefär en fjärdedel genom att minska kapslarnas bredd med 48 layoutenheter och den yttre sidpaddingen från 4 till 3; högerkant, texter och textstorlek behålls. Marknads- och teamdiagrammens procentetiketter är villkorsfärgade: positiva gröna och negativa röda.

Den senaste rapporten är schemavaliderad utan fel eller varningar, omladdad och granskad i Desktop. Bildkontrollen bekräftar att alla tre kapslar visar hela texter utan tom slutsektion eller scrollbar, samt gröna positiva marknadstal och Finlands röda negativa tal. Tillfälliga skärmbilder rensas efter kontrollen.

Valideringsverktyget v0.5.0 hade ett falskt fel för `labels.detailColor.solid.color.expr`: bäraren `solid.color` tolkades som en nästlad formateringsinställning. De lokala CLI-filerna har en snäv rättning som känner igen just denna giltiga färgbärare; schemavalidering och kontroll av vanliga nästlade inställningar behålls. Om verktyget installeras om behöver denna rättning omprövas.

## Säljarlistan närmare referensen

Tre separata rundade rader följer referensens hierarki. Aubecos blå färg används för namn, initialmärken och staplar. Segmentens längd avser säljarens omsättning relativt förstaplatsen. År och månad styr hela rankningen. Vid lika omsättning avgör säljarens tekniska nyckel ordningen, så att det alltid finns högst tre namngivna rader. Perioder med färre än tre aktiva säljare lämnar återstående mått tomma.

TMDL är parsad med TOM och PBIR är validerad utan fel eller varningar. Faktisk DAX i Desktop ger Leo Palm, Alice Sjö och Ebba Dal för 2025: 949 993,08 / 864 208,11 / 824 070,04 kr och +45,0 / +7,0 / +1,7 %. Deras gemensamma andel är 17,2 %. Resultaten finns i `validation/desktop-seller-cards.json`.

Första bildkontrollen visade ärvda vita bakgrunder i de små korten och avkortade segment. Detta är rättat och verifierat i den senaste Desktop-bilden. Initialmärkena använder dynamiska initialer, inte porträtt.

## Produktdiagram – senaste korrigering verifierad

Produktvalet är flyttat 32 layoutenheter upp, till höger om rubriken. Rubriken har smalare textruta så att den inte överlappar togglen. Produktdiagrammet har fått mer höjd. En dold dynamisk skalgräns, `Produktaxel max`, ger 28 % marginal utöver den största produktens valda värde. Marginalen följer datumfilter och växlingen mellan omsättning och enheter; en fast beloppsgräns används inte. TMDL och PBIR är validerade. Faktisk DAX i Desktop ger 1 745 770,44 som största produktbelopp och 2 234 586,1632 som skalgräns; för enheter är motsvarande värden 1 151 och 1 473,28. Resultat: `validation/desktop-product-axis.json`. Bildkontrollen bekräftar hela belopp efter samtliga fem staplar, även den längsta.

## Kompaktare togglar enligt referensen

Referensens kapslar uppskattas till ungefär 26 bildpixlar höga. Detta är en uppskattning från de bifogade bilderna, inte ett verifierat källmått. På rapportens 1920 × 1080-canvas är de nya togglarna 40 layoutenheter höga i stället för 56, motsvarande ungefär 29 bildpixlar vid 1400 pixlars sidbredd. Bredderna är 200 för Månadsutveckling, 176 för Land/Kategori och 224 för Produktval. Olika bredder ger plats för svenska etiketter utan minskad textstorlek. Alla tre behåller sin högerkant och är vertikalt centrerade i den tidigare placeringen.

Inre vertikal padding är 0, horisontell padding 4 och yttre padding 2, vilket undviker höjdklippning i den mindre storleken. Den slutliga Desktop-bilden visar hela texter, sammanhängande kapslar och inga scrollbars. Säljarlistan, produktetiketterna och de båda vita kortens gemensamma underkant är också kontrollerade. PBIR-valideringen ger noll fel och varningar. Tillfälliga kontrollbilder rensas efter granskningen.

## KPI-kort närmare referensen – verifierade i Desktop

Rubrikerna är större, huvudvärdena har samma vänsterkant som rubrikerna och förändringarna ligger på en rad under värdena. Svenska textmått visar plus/minus och ▲/▼, med villkorsstyrd grön/röd färg. Faktisk DAX för 2025 ger +16,4 % ▲, +17,8 % ▲, +23,4 % ▲, +1,5 pp ▲ och +18,1 % ▲. Resultat: `validation/desktop-kpi-labels.json`.

Desktop-bilden visade horisontella scrollister under samtliga fem trendytor. En minskad kategoribredd räckte inte för att ta bort dem. Trendytorna använder nu `Datum.Månadsnummer` på en kontinuerlig (`Scalar`) axel, med stigande månadssortering och explicit avstängda zoomreglage. Det ger samma månadsaggregering och låter årets punkter rymmas utan kategorisk scrollbar.

Jämförelsetexten är återställd till `Årsförändring:` enligt användarens önskemål. Texten har 84 layoutenheters bredd och förändringsvärdet börjar vid kortets x+116, direkt efter texten. Fullständig förklaring, "Förändring mot samma period föregående år", finns i textens alt-text. Svenska tecken, procentenheter och villkorsfärger behålls.

Den senaste rapporten är PBIR-validerad utan fel eller varningar, omladdad och granskad i Desktop. Samtliga fem trendytor syns utan scroll- eller zoomreglage. Alla fem procent-/piltexter syns på den avsedda vänstra positionen. Tillfälliga kontrollbilder rensas efter granskningen.

För att trendytorna ska utnyttja sin fulla bredd har den kontinuerliga månadsaxeln explicit start 1 och slut 12, med avstängd avrundning av intervallet. Automatisk avrundning skapade tidigare tom yta efter december. Den senaste Desktop-bilden bekräftar bredare trendytor i alla fem kort, utan scrollister och med återställd jämförelsetext. Ytterkortens storlek och huvudvärdenas placering behålls.

## Säljarlistans etiketter och riktningspilar

Belopp, separator och förändring ligger nu närmare den segmenterade stapeln på samma rad, med namnet ovanför. Förändringen visar exempelvis `+45,0 % ▲ mot föreg. år`. Positiva värden får grön uppåtpil, negativa röd nedåtpil och noll ett streck. Färgregeln använder det numeriska förändringsmåttet, medan etiketten är svensk text.

PBIR och TMDL är validerade. DAX-kontrollen omfattar helåret 2025 och årets tolv månader, med resultat i `validation/desktop-seller-labels.json`. Desktop-bilden bekräftar hela belopp, separatorer och gröna piltexter i alla tre säljar­rader utan överlappning. Dessa testperioders topp tre hade positiva förändringar; negativ färg och pil är definierade men visades inte i den granskade bilden.
