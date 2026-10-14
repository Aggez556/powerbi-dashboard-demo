# Aubeco: återanvändbar designguide för Power BI

Analyserad 2026-10-06 från [aubeco.se](https://www.aubeco.se/). Guiden avser grafisk profil och återanvändbara komponentregler. Den bestämmer inte rapportens innehåll, nyckeltal eller sidor. Inga dummydata, semantiska modeller eller rapporter har skapats.

**Designläsning:** svensk verksamhetsnära BI med lugnt, maritimt formspråk, geometriska rubriker, mörkblå struktur och varm orange betoning. Power BI-anpassningen använder ljusa analysytor och tydlig numerisk hierarki.

Taste har använts för att läsa den befintliga identiteten och undvika generisk formgivning. Dess webbspecifika rekommendationer om animationer och frontendbibliotek tillämpas inte på rapporten. Microsofts installerade `powerbi-report-cli` styr typografi för data, diagram, layout, kontrast och temamekanik. Ingen semantisk modell finns att inspektera i denna fas; sidlayout och färgkoppling till mått bestäms senare utifrån verkliga krav.

## Evidens och säkerhetsnivå

- **Verifierat:** värden som finns i hämtad CSS/HTML, uppmätt computed style eller originalbildens pixlar. Detta verifierar webbplatsen vid analystillfället, inte en officiell varumärkesmanual.
- **Tolkning/uppskattning:** bedömningar av uttryck, balans, hierarki och önskad känsla. Dessa är inte Aubecos fastställda regler.
- **Rekommenderad anpassning:** nya Power BI-värden för läsbarhet, komponenter och layout. Exakta rekommendationer är fortfarande designbeslut, inte verifierade originalvärden.

Källfiler finns i [sources](../assets/aubeco/sources/manifest.json), med URL, innehållstyp och SHA-256. [Original-CSS](../assets/aubeco/sources/04e247_t1fs-p.css) har även en [läsbar kopia](../assets/aubeco/sources/04e247_t1fs-p.css.readable.txt). [Desktopmätning](../assets/aubeco/sources/computed-desktop.json) avser Edge, 1440 × 1000 CSS-pixlar, skalfaktor 1. [Mobilmätning](../assets/aubeco/sources/computed-mobile.json) avser 390 × 844. Måtten nedan gäller dessa vyer och ska inte presenteras som fasta mått för alla skärmar.

## Verifierade färger

Samtliga namngivna färger i följande tabell finns i CSS-lagrets `:root,:host` under `--color-*`. Rollbeskrivningen bygger på namnen och observerad användning på startsidan.

| CSS-token | Exakt färg | Observerad/avsedd roll |
| --- | --- | --- |
| navy | `#0F3163` | Rubriker, blå sektioner och länkar |
| navy-deep | `#09224A` | Heroöverlägg, sidfot och mörk struktur |
| navy-700 | `#1C438F` | Blå övergångar och dekoration |
| navy-500 | `#4A6BCE` | Ljusare blå accent/gradient |
| orange | `#F7BA6B` | Webbens ordmärke, CTA och betoning |
| orange-bright | `#FFC888` | Ljusare CTA-hover |
| orange-soft | `#FBD6A8` | Mjuk orange stödton |
| sand | `#FAEBD7` | Varma ljusa stödytor |
| sand-soft | `#FDF6EC` | Ljusa sektionsbakgrunder |
| ink | `#0B1B30` | Primär brödtext |
| muted | `#5B6B80` | Sekundär text |
| white | `#FFFFFF` | Ljusa ytor och text på mörkt |

CSS innehåller också gradientstopp `#FFB65B` och `#6B8BE4`. Bakgrundsgradienten är `120deg`, med `#0F3163` vid 0 %, `#1C438F` vid 38 %, `#4A6BCE` vid 64 % och `#FFB65B` vid 100 %. Dessa definitioner är verifierade; alla behöver inte vara aktiva i varje sektion. Det dekorativa rutnätet är 48 × 48 px med vita linjer vid ungefär 5 % opacitet (`#FFFFFF0D`).

Fotografiernas havs-, klipp- och skogstoner ger kompletterande stämning. Ingen färg har uppskattats från fotografier för att användas som primär profilfärg.

## Verifierad typografi och vikter

| Roll | CSS och mätning | Power BI-anpassning |
| --- | --- | --- |
| Rubriker och ordmärke | `echotun`; fil `AubecoRegularv4-s.p.2oo_yfe6ak6tv.woff2`; deklarerad vikt **400** | Behåll originalet i logotypen. Segoe UI Semibold för rapporttitlar och KPI-värden |
| Brödtext | Open Sans; variabel font med intervallet **300–800**, normal stil | Segoe UI Regular för axlar, filter, tabeller och etiketter |
| CTA | Open Sans **700**, verifierat i computed style | Segoe UI Semibold/Bold, endast för korta åtgärder |
| Navigation | HTML-klassen `font-semibold` motsvarar CSS **600** | Segoe UI Semibold för filterrubriker |

`.font-heading` sätter `font-weight:400` och `letter-spacing:-.01em`. `.font-heading.font-bold` sätter uttryckligen också **400**. HTML-klassen `font-bold` får därför inte tolkas som verklig vikt 700 för dessa rubriker. Browsern visar laddad `echotun`-font och vikt 400 för både H1 och ordmärke.

Vid 1440 px bredd är rotstorleken **14,5 px**. CSS använder `clamp(.875rem,.625rem + .3125vw,1rem)` från 64 rem. H1 är **65,25 px**, radavstånd **68,5125 px** (1,05), bokstavsavstånd **−0,6525 px**. H2 är **32,625 px**, radavstånd **40,7812 px** (1,25). Hero-brödtexten är **18,125 px**, vikt **400**, radavstånd **29,4531 px** (1,625). Vid mobilbredd är roten **16 px** och H1 **36 px**. CSS-pixlarna är inte Power BI-punkter och kopieras inte direkt till rapporten.

**Alternativa typsnitt:** echotun → Segoe UI Semibold; därefter Arial Bold om miljön kräver ett annat vanligt sans-serif. Open Sans → Segoe UI Regular; därefter Arial Regular. Open Sans kan behållas om det finns tillgängligt och har testats i samtliga målmiljöer. Echotuns och Open Sans specifika former är inte identiska med alternativen; detta är en medveten kompatibilitetsanpassning.

Det levererade temat använder konkreta fontnamn, Segoe UI och Segoe UI Semibold. JSON-temat bäddar inte in webbens WOFF2-filer. Fontfamilj i CSS är inte i sig bevis på tillgänglighet i Power BI. Originalfontens interna installationsnamn och licens för vidare distribution har inte verifierats; inga fontfiler har laddats ned eller installerats. Kontrollera Desktop, Service, mobil och PDF-export innan originaltypsnitt används. Typsnittsersättningar ska anges uttryckligen, inte lämnas åt tyst substitution.

## Logotyp

[Hämtad originalbild](../assets/aubeco/aubeco-original.png) från [Aubecos bildfil](https://www.aubeco.se/aubeco-google-bild.png), **1351 × 1007 px**, PNG med mörk bakgrund. HTML:s strukturerade organisationsdata anger samma fil som `logo` och social bild.

Verifierad pixelanalys visar bakgrund **`#003267`** och ordmärke **`#FFB65B`**; [mätresultat](../assets/aubeco/sources/logo-image-evidence.json). Dessa skiljer sig från webbens primära CSS-tokens. Originalbilden är sparad oförändrad och har inte färgats om eller gjorts transparent.

Webbens header använder däremot texten `aubeco` i echotun med CSS-färgen `#F7BA6B`, inte en fristående logotypbild. Ett [skärmutklipp](../assets/aubeco/sources/web-wordmark-reference.png) dokumenterar detta, men innehåller den bakomliggande webbytan och är endast en visuell referens. [Favicon](../assets/aubeco/favicon-original.png) är också hämtad.

**Tolkning:** gemena, geometriska bokstavsformer med rundade öppningar gör ordmärket vänligt och tydligt. Bokstävernas former ska inte återskapas med ett ersättningstypsnitt som logotyp.

**Rekommendation:** använd originalbilden med bevarat bildförhållande cirka **1,342:1**. Den har stor inbyggd luft och är inte ett tätt beskuret, transparent ordmärke. För en kompakt rapportheader behövs därför helst en officiell transparent PNG eller SVG från Aubeco; originalet kan tills vidare användas som en separat logotypyta. Rekommenderad friyta är minst en halv bokstavshöjd kring själva ordmärket, men detta är en uppskattad regel, inte en verifierad brandmanual. Skala proportionellt, håll den utanför dataområdet och använd inte logotypbildens bakgrund som en ny generell rapportfärg.

## Mellanrum, hierarki och formspråk

| Egenskap | Verifierad webbkälla | Tolkning och Power BI-anpassning |
| --- | --- | --- |
| Grundsteg | `--spacing:.25rem`, 3,625 px vid desktopmätningen och 4 px på mobil | Rapporten använder ett eget **8 px-raster** för konsekvent placering |
| Yttre struktur | `max-w-[96rem]`, `px-5 sm:px-8`; H1 och logotyp börjar vid x=53 px i desktopvyn | Vänsterförankrad struktur; rekommenderad rapportmarginal **32 px** på FHD |
| Luft mellan sektioner | Exempel `pt-28`: **101,5 px** i desktopvyn; `pb-16`: **58 px** | Generös webbrytm; använd **24–32 px** mellan analysgrupper |
| Kort | Tjänstekort `rounded-2xl`: **14,5 px** radie, `sm:p-10`: **36,25 px** padding; mobil **16/32 px** | Rapportkort: **8 px** radie och **16 px** avsedd innehållsluft |
| Fotoyta | `rounded-3xl`: **1,5 rem** | Behåll mjukhet i containers; undvik dekorativa foton bakom diagram |
| CTA | `rounded-full`, orange fyllning, mörkblå text; **25,375/12,6875 px** horisontell/vertikal padding desktop | Avrundad knapp för viktiga åtgärder, inte som omslutning av varje filter |
| Skugga | `0 10px 30px -18px rgba(8,31,63,.35)` | Webbens djup ersätts med luft och diskreta linjer; rapportskuggor avstängda |
| Betoning | Små versala sektionsetiketter, större geometriska rubriker, varm orange CTA | Storleken på KPI-värdet prioriteras; vanliga ord för filter och diagramrubriker |

**Tolkning:** mörka, fotografiska sektioner växlar med vita och sandfärgade ytor. Stora ytor, rundade kort och knappar, tunna linjer samt havsbilder ger en varm men strukturerad identitet. Rutnät och flödesgrafik signalerar dataplattformar. Dessa observationer beskriver startsidan, inte en fastställd regel för alla Aubeco-material.

**Rapportens signatur:** ljus sandfärgad canvas, vita analysytor, mörkblå rubriker och sparsam orange betoning i den gemensamma headern. Mörkblå header och orange markör är rekommenderade manuella komponenter; temat skapar dem inte. Fotobakgrunder, dekorativa rutnät, hoverförflyttningar och gradienter ersätts av stabila, rena dataområden.

## Power BI-tokens och kontrast

| Användning | Värde | Status |
| --- | --- | --- |
| Canvas | `#FDF6EC` | Verifierad färg, ny rapportroll |
| Visualyta | `#FFFFFF` | Verifierad färg, ny rapportroll |
| Primär text | `#0B1B30` | Verifierad |
| Rubrik/primär serie | `#0F3163` | Verifierad färg, rapportanpassad roll |
| Sekundär text | `#5B6B80` | Verifierad |
| Orange dekor på mörkt | `#F7BA6B` | Verifierad |
| Orange data/text på ljust | `#9B570B` | **Ny, rekommenderad mörkare variant**, inte Aubecos CSS |
| Linjer/avgränsare | `#D5DDE7` | **Ny rekommenderad neutral** |
| Positiv status | `#007956` | Finns som CSS `emerald-700`; användning som rapportstatus är rekommenderad, inte en verifierad profilregel |
| Varning | `#946200` | **Ny rekommenderad statusfärg** |
| Negativ status | `#B42318` | **Ny rekommenderad statusfärg** |

[Kontrastkontrollen](../themes/validation-result.json) använder sRGB:s relativa luminans, utan transparens eller bildbakgrund.

| Kombination | Kontrast | Regel |
| --- | --- | --- |
| Ink på vitt | **17,30:1** | Primär text |
| Navy på sand-soft | **11,93:1** | Rubriker |
| Muted på vitt / sand-soft | **5,44:1 / 5,07:1** | Sekundär text |
| Orange på navy-deep | **9,10:1** | Profilbetoning på mörk header |
| Originalorange på vitt | **1,72:1** | Otillräckligt för text och informationsbärande diagrammarkeringar |
| Anpassad orange på vitt | **5,58:1** | Läsbar ersättning för diagram och text |

Normal text ska ha minst **4,5:1**, informationsbärande linjer och markeringar minst **3:1** mot sin bakgrund. De fyra temaserierna har minst 4,90:1 mot vitt. Detta är inte ett test av färgseende eller ett bevis på att serierna alltid går att skilja från varandra; använd etiketter, markörer och linjemönster och begränsa antalet samtidiga serier. Ljusa stödlinjer behöver inte bära information själva; viktiga referenslinjer ska använda muted eller navy.

## Återanvändbara komponentregler

Alla värden i detta avsnitt är **Power BI-rekommendationer**.

### Typografisk skala

| Roll | Storlek i Power BI | Typsnitt/vikt | Färg |
| --- | --- | --- | --- |
| Sidtitel | **20 pt** | Segoe UI Semibold, cirka 600 | Navy på ljust, vitt på mörkt |
| Visualrubrik | **14 pt** | Segoe UI Semibold | Navy |
| KPI-värde | **32 pt** | Segoe UI Semibold/Bold, cirka 600–700 | Navy |
| KPI-etikett, axel, legend, filter, not | **11 pt** | Segoe UI Regular; filterrubrik semibold | Ink eller muted |

För dessa roller används fyra storleksnivåer. Temats `header`-klass är 12 pt för de inbyggda visuella roller som använder den; den är inte rapportens sidtitel. Kritiska etiketter får inte krympas för att passa för mycket innehåll. Webbens tracking, line-height och variable-font-inställningar saknar direkt motsvarighet i de primära temaklasserna.

### KPI-kort

- Kort etikett, stort värde och en separat jämförelse med period eller mål. Visa enhet och aktuell tidsperiod. Ingen ensam siffra utan kontext.
- Mörkblått värde på vit yta. Orange får vara en liten markör på mörkt; mörk orange används om markören eller texten ligger på vitt.
- Rundning 8 px, diskret kant, inga skuggor. Modern `cardVisual` har noll containerpadding och noll callout-padding i temat för att undvika dubbel padding; avsedd 16 px luft ordnas i visualens layout vid rapportbygget.
- Avstånd mellan kort 16–24 px; antal kort bestäms av verkliga beslut som ska stödjas. Statusfärg kompletteras alltid med text eller ikon. Ett positivt numeriskt delta är inte automatiskt bra, exempelvis för kostnader.
- Formatera enligt `sv-SE`: decimal med komma, grupperade tusental, procent med tydlig precision och enhet som kr, tkr eller mnkr efter behov. Talformat sätts i mått/visualer, inte automatiskt av temat.

### Diagram och tabeller

- Börja med navy för primärt mått. Vid samtidiga serier används ordningen **navy, mörk orange, navy-500, muted**. Samma mått ska få samma färg över sidor; den bindningen fastställs senare, eftersom ingen modell finns ännu.
- Linjediagram för kontinuerlig tid, sorterade horisontella staplar för jämförelse/rankning och tabell för exakt avläsning. Välj först efter frågan, sedan efter formen på data.
- Staplar har nollbaslinje. Linjer är raka mellan observationer och 2,5 px tjocka; inga utjämnade kurvor som antyder oobserverade värden. Ingen 3D eller dekorativ områdesfyllning.
- Rubrik 14 pt, axlar/legend/datavärden 11 pt. Visa bara etiketter som inte krockar; behåll axlar när de behövs för tolkning. Temats stapelstandard bygger på avläsning via dataetiketter, men täta diagram kan kräva visad värdeaxel i stället.
- Direktetikettera när möjligt. För fler än fyra kategoriska serier: filter, små multiplar eller grupperad kategorisering; låt inte automatiskt genererade extrafärger bli en ny profilpalett.
- Tabeller: navy-rubrik/ink-text, vita och sand-soft-rader, anpassade kolumnbredder, högerställda tal. Radbandning är stöd, inte betydelsekodning.

### Filter och navigation

- Reservutrymme för sidtitel och 1–3 viktigaste filter. Vid fler filter används en tydlig sidopanel. Visualer får inte ligga bakom kontrollerna.
- Dropdown för längre kategorilistor; få tydliga alternativ kan visas som knappar. Välj år/månad/datumgranularitet efter frågan, inte efter vilket datumfält som råkar finnas.
- Vit yta, ink-text, navy-rubrik, 11 pt, cirka 40 px höga klickytor som rekommendation. Synligt aktuellt urval och tydlig åtgärd för återställning.
- Orange markerar val/åtgärd, inte varning. På ljus bakgrund krävs mörk text eller en mörk markeringskant. Ersätt inte en synlig vald etikett med enbart färg.
- Tangentbordsordning: titel → filter → KPI → diagram → detalj. Behåll möjlighet till informationsmeny, export eller fokusläge där användaren behöver det; temat döljer visual headers som standard, och nödvändiga funktioner ska då exponeras manuellt.

### Layout

Utgå vid senare nybygge från **1920 × 1080**, 32 px marginaler, 24 px mellan analysgrupper och 16 px inom en grupp, på 8 px raster. Detta är rekommendationer från Power BI-skillen, inte Aubecos webb-CSS. Rapportstorleken, sidantalet och varje sidlayout låses först när innehållet är bestämt. Testa alltid läsbarhet i verklig visningsstorlek och bygg separat mobillayout vid behov.

## Tema, validering och gränser

[Importbart Power BI-tema](../themes/aubeco-powerbi.json). Det utgår från den installerade Microsoft-skillens bas och bevarar textbox-undantag, `cardVisual`-padding/spacing samt tabellernas grow-to-fit. Temat sätter palett, strukturfärger, typografiska klasser, vita visualytor, sand-soft-canvas, kanter, diagramstandarder och slicertext. Det skapar ingen rapport och registreras inte i PBIP ännu.

Temat använder [Microsofts officiella schema 2.157](https://github.com/microsoft/powerbi-desktop-samples/tree/main/Report%20Theme%20JSON%20Schema), exploration version **5.76**. GitHub-katalogen hämtades live och den högsta publicerade versionen valdes, eftersom inget befintligt Desktop/PBIP-bastema finns i projektet. [Originalschemat](../themes/schema/reportThemeSchema-2.157.json) och [katalogen](../themes/schema/catalog.json) är sparade lokalt. En äldre Desktop-version kan behöva sitt matchande schema och ny validering.

**Resultat:** Ajv **8.20.0**, Draft-07-validering, **0 temafel**. Originalschemat innehåller en duplicerad enum-post i `actionStates-advancedSlicerVisual`. Valideringsskriptet deduplicerar identiska enum-värden endast i minnet, vilket bevarar exakt samma tillåtna värdemängd. Inga temakrav har stängts av och originalschemat är oförändrat. SHA-256 och justeringen finns i [valideringsresultatet](../themes/validation-result.json).

Detta är schema- och kontrastvalidering, **inte** verifierad import/rendering i Power BI Desktop. Sidhuvud, logotypplacering, filterlayout, KPI-kontext, talformat, villkorsstyrd formatering, faktisk fontsubstitution, alttexter och läsordning kräver senare rapportarbete. Per-visual-inställningar kan dessutom överstyra temat. [Microsofts temadokumentation](https://learn.microsoft.com/en-us/power-bi/create-reports/report-themes-create-custom) beskriver färger, textklasser, visualStyles och schemaimport.

Återupprepa valideringen från projektroten:

```powershell
node scripts/validate-aubeco-theme.cjs
```

För att återskapa temat från designbesluten:

```powershell
python scripts/build-aubeco-theme.py
node scripts/validate-aubeco-theme.cjs
```

## Återanvändbar designidentitet

Detta är en identitetsmall, inte ett godkänt sid- eller rapportkontrakt. Inga fältbindningar eller sidor uppfinns före krav och dataanalys.

```yaml
Design Brief:
  generated_by: powerbi-report-cli
  contract_version: 1
  mode: greenfield
  phase: brand_profile_only
  design_identity:
    tone: Lugn svensk verksamhetsanalys med maritim mörkblå struktur och varm orange betoning
    signature: Sand-soft canvas och vita analysytor med mörkblå typografi och sparsam orange headerbetoning
  theme_file: themes/aubeco-powerbi.json
  font_strategy: Segoe UI för data och Segoe UI Semibold för hierarki
  canvas_recommendation: { width: 1920, height: 1080, margin: 32, gutter: 24, snap: 8 }
  color_map_status: Bestäms när mått och jämförelser är kända
  pages: []
  implementation_status: Dummydata och rapportbygge väntar
```
