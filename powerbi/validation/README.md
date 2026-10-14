# Valideringsstatus

Kontroller genomförda 2026-10-06. Ingen publicering eller kontakt med en Fabric-arbetsyta har gjorts.

| Kontroll | Verktyg och resultat | Begränsning |
|---|---|---|
| PBIP/PBIR, tema och visualegenskaper | Microsoft powerbi-report-author 0.5.0, officiella JSON-scheman: 0 fel, 0 varningar. Se pbir-result.json. | Bevisar inte att Desktop kan rendera varje visual. |
| TMDL | Microsoft TOM 19.84.1: deserialisering lyckad; fyra tabeller, tre many-to-one/OneDirection-relationer, Import-partitioner och markerad datumtabell. Se tmdl-result.json. | Kör varken Power Query eller DAX och processar ingen modell. |
| Dummydata | Python och SQLite: rätt radantal, unika primärnycklar, giltiga främmande nycklar, sammanhängande kalender, konsekventa order och exakta monetära identiteter. | CSV-data, inte inläst Desktop-data. |
| Måttförväntningar | Oberoende SQL-aggregering i heltalsören för år, kategori och månad. Se data-and-measure-expectations.json. | Jämförelsevärden; ingen faktisk DAX-motor körd. |
| Fält och layout | Alla projektioner matchar namn i TOM:s modellmetadata. 21 visualer ligger inom sidornas 1920×1080 och överlappar inte. | Geometri och bindningar verifierade; etikettklippning, fontåtergivning och interaktion behöver Desktop. |
| Reproducerbarhet | CSV-filer matchar SHA-256 i data/manifest.json, med fast seed. Omkörning ger samma filer. | Generatorerna skriver över levererade artefakter. |
| Desktop: inläsning, DAX och skärmbilder | Inte genomförd: Desktop hittades inte och ingen ansluten Power BI-motor fanns. | Följ ../README.md för installation, öppning, uppdatering och jämförelse. |

Försäljningens 10 000 rader representerar 4 000 order. Alla 100 kunder och 30 produkter förekommer. November–december har 2 498 orderrader, juni–juli 1 435. Datakalendern har 731 datum. 2024 har omsättning 11 596 424,01 kr och 1 829 order; 2025 har 13 818 582,35 kr och 2 171 order.

Det registrerade rapporttemat är en kompatibilitetsanpassad kopia av det tidigare skapade temat. Kortens containerinställningar anges på respektive visual eftersom CLI:s metadata tolkar tre kortobjekt annorlunda än det generella temaschemat. Detta klarar både schemavalidering och CLI:s egenskapskontroll. Faktiskt visuellt resultat återstår att granska i Desktop.
