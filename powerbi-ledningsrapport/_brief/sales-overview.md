# Försäljningsöversikt – genomförd utökning

Användarens senaste beställning utökar tidigare tvåsidiga omfattning till Start, Ledningsöversikt och Försäljningsöversikt. Endast den nya analyssidan byggs. Företagsnamn och logotyper ska saknas överallt. Ingen publicering ingår.

Referensbilden styr dispositionen; det befintliga temat styr sandfärgad canvas, vita paneler, mörkblå text och Segoe UI. Sidan har sex kort i en rad och två kolumner × två analysrader, sidonavigation och tre filtergrupper. Samtliga dataobjekt är native Power BI-visualer. Canvas 1920 × 1200.

Standard är R12 september 2026, Alla områden. Enligt den senaste instruktionen använder även Ledningsöversikten september som sparad standardmånad och vid byte av periodtyp. Periodval återanvänder samma frikopplade periodtabeller och DAX-regler. Områdesvalet har fyra alternativ, påverkar både aktuella och föregående värden och ändrar kort 5–6 enligt specifikationen.

Modellen utökas med artikel/kategori, kundbransch, produktorder och timdebiteringsrader. Det finns inga duplicerade intäktsfakta. Kontroller av sammanhängande månads-, kategori-, bransch- och områdessummor samt bevarad resultatbrygga finns i validation. Läs README för den dokumenterade omfördelningen av föregående periods intäkt och lika stora kostnad mellan service och bemanning.

Nästa verifieringssteg efter filkontroller är faktisk import, DAX-körning och renderad granskning i Desktop. Dessa får inte redovisas som genomförda enbart på basis av datagenerator eller schema.
