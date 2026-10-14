# Ekonomi och lönsamhet – referensgranskning

Referensen styr komponenttyper, proportioner och placering. Aubecos färger, svenska och befintliga nordiska marknader behålls. Canvas 1920 × 1080: KPI-rad y=276–476; månadsdiagram x=320–1272, y=488–784; marknadskort x=320–1272, y=808–1064; högerkort x=1296–1864, y=488–1064. År och Månad följer Ledningsöversikten.

## Granskning kort för kort

| Del | Jämförelse och korrigering |
| --- | --- |
| Bruttovinst | Vänsterjusterat belopp, kompakt årsförändring med färgad triangel och bred diskret trendyta. |
| Bruttomarginal | Samma placering; förändring i procentenheter. |
| Varukostnad | Samma placering; kostnadsökning är röd med uppåtpil. |
| Omsättning per enhet | Samma placering; kr och röd nedåtpil vid minskning. |
| Bruttovinst per enhet | Samma placering; kr och grön uppåtpil vid ökning. |
| Månadsutveckling | Tre modellstyrda native diagram, kompakt Kategori/Team-val, gruppnamn till höger, gemensam dynamisk Y-skala, separata medellinjer med Medel-etikett och diskret skuggning ovanför. J F M A M J J A S O N D i båda lägena. Fast månadsnummeraxel med separata kalenderinitialer undviker horisontell scrollbar. |
| Vinstfördelning | Fyra tunna staplar med grå bakgrund; marknad, belopp och andel på separata rader ovanför. |
| Lönsamhet per marknad | Dropdown Land/Kategori styr tabell och rubrik. Fasta kolumnbredder; centrerad bruttovinst, årsförändring och marginal; datastaplar, färgade trianglar, små marginaldiagram och trendlinjer med slutpunkt. Separat från månadsdiagrammets val. |
| Topp 5 produkter | Tunna staplar med lika långa grå bakgrunder, separat beloppskolumn och modellstyrd topplista. Dynamisk skalreserv fungerar även i oktober. Andel i underrubriken. |
| Bruttovinst jämfört med varukostnad | Mindre ihåliga punkter, tre kategoriers färger, svenska axlar och separata medelkostnads-/medelvinstlinjer. |

Kategori består av Elektronik, Hem och kök samt Övrigt (Kontor, Sport och fritid, Trädgård). Alla produkter ingår. Ingen produktdetaljlänk utan destination eller specialdesignad tooltip-sida har lagts till.

## Verifiering

- PBIR: 334 visualiseringar, inga fel eller varningar. Microsoft TOM parsar nio Import-tabeller och fyra enkelriktade relationer. Calculate i Desktop utan måttfel; ingen ny import av källdata.
- Nya Desktop-bilder har öppnats och granskats efter omladdning: helår/Team/Land, helår/Kategori/Land och oktober/Kategori/Kategori. Hela sidan kontrollerades, inklusive läsbarhet, staplar, belopp, marginalindikatorer, medellinjer och gemensamma nederkanter.
- DAX och oberoende CSV-kontroll: helår 2025, oktober, september–oktober och 96 ursprungliga grupp-/månadskombinationer. Senaste DAX-kontrollen verifierar också 72 panel-/månadskombinationer (tre paneler × tolv månader × två lägen): gemensamt skalmaximum, konstanta gruppmedel och bibehållen totalvinst. Befintliga valutamåtts precision beaktas.
- Sammanställningens fyra länder och tre kategorigrupper verifierades med DAX; båda summerar till 4 096 778,32 kr. Dropdownen provades genom faktisk Desktop-interaktion tidigare i genomgången; kategoriresultatet bildgranskades.
- Senaste automatiska klickförsöken på segmentväljaren kunde inte bekräfta ändrat UI-tillstånd. Slutlig bildkontroll av kategori och oktober gjordes därför med explicit filterkontext på disk och omladdning, inte som ett godkänt klicktest. Tillfälliga val återställs till 2025, Alla månader, Team och Land före leverans.
- Positiva/negativa förändringar och tom period kontrollerades med DAX. Tomma presentationstexter ersätter påhittade nollvärden. Standardverktygstips använder modellvärden.

Originalets andra produktnamn, engelska och lila profil ersätts med projektets data och Aubecos stil. Inget publiceras.

Efterföljande etikettkorrigering: månadsdiagrammens fasta X-intervall reserverar två tomma positioner till höger om december. Medel-etiketten ligger i denna reserverade yta och kan inte täckas av en månadsstapel. Kalenderinitialerna följer den justerade skalan. Kategori och Team bildgranskas efter omladdning.

Diagramavstånden har därefter minskats genom att ta bort reserverat utrymme för dolda Y-axlar i panel två och tre. Diagrammen får bredare stapelyta med smalare mellanrum; baslinjer och kalenderetiketter justeras till samma placering. Medel-etiketternas reservyta behålls.

Grupprubrikerna i Månadsutveckling är centrerade enligt användarens senaste instruktion, för både team och kategori.
