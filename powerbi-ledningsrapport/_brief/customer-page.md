# Kunder – lokalt genomförande

Användaren har uttryckligen godkänt att Kunder byggs enligt den bifogade bilden, med dashboard-planen som underlag. Senaste chattspecifikation har företräde framför dokumentets äldre omfattning. Endast Kunder läggs till; Budget och Projekt / beläggning förblir framtida sidor. Företagsnamn och logotyper ska fortsatt saknas. Publicering ingår inte.

Sidan återanvänder sandfärgad canvas, vita paneler, mörkblå Segoe UI-rubriker, sex KPI-kort och fyra native analysvisualer. Canvas är 1920 × 1200 med FitToPage. Bransch filtrerar sidan. Statusfiltret styr bara uppföljningstabellen; klick i diagram eller kundtabell får inte räkna om övergripande churn.

Standard: R12 september 2026. Helår erbjuder avslutade år 2024 och 2025. I månadsläget följer hela kundanalysen R12 till vald månads slut, tydligt angivet i periodtexten. Därför begränsas denna sidas månadsväljare till december 2024 och senare, där två kompletta R12 finns. Övriga sidors månadsväljare behåller sina egna periodregler.

Kundkohorter fastställs för hela analysperioden och hela kundrelationen. Samma kohort används i alla månadsstaplar. Historiskt första köp finns som metadata för de fem återaktiverade kunderna före transaktionshistorikens början. Krediter skapar inte aktivitet. Demokrediter knyts till en befintlig köpare så att även historiska kohortintäkter summerar till total nettoomsättning.

Underlaget har balanserats med deterministisk proportionell anpassning och exakt heltalsavrundning via nätverksflöde. Varje månads-, områdes-, artikel-, debiteringstyps- och branschtotal bevaras. Fördelningen uppfyller 35 helt nya, 5 återaktiverade, 10 förlorade samt intäktsbryggan 120 − 4 − 18 + 12 + 27 + 2,5 = 139,5 Mkr. Kostnader som kan hänföras till kunder fördelas på samma befintliga direkta kostnadsfakta med spårbar fördelningsnyckel. Ej uppdragsfördelad personal ligger kvar med kundnyckel 0 och ingår i områdets ekonomiska utfall.

Uppföljningstabellen visar sju kunder med störst försäljning/förändring inom vald status. Det ger en användbar lista som ryms utan scrollning. Klick på en rad visar bransch, köpta områden, absolut förändring och kundens hänförliga bruttovinst i detaljrader under tabellen. Kundmarginalen inkluderar endast kundens hänförliga kostnader.

Verifiering: `validation/customer-independent-checks.json` innehåller 24 period-/branschfall och exakta standardvärden. Befintliga försäljnings- och ledningskontroller körs separat. Efter rättning av ett reserverat DAX-variabelnamn har full import nu slutförts i en nyöppnad Desktop-session. `validation/customer-live-verification.json` verifierar faktiska DAX-resultat för KPI, bryggbelopp, fem branscher, helår 2024/2025, R12-kundanalys vid månadsval, månadstrend och förlorade kunders tabellfilter. Uppdaterad datacache har sparats genom Desktop. Renderad granskning redovisas separat.
