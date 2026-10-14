# Realistiska produktnamn

Alla 30 namn i DimProduct.csv ersätts med konkreta svenska produktnamn som passar respektive kategori. Produktnycklar, kategorier, listpriser, standardkostnader och marginaler behålls. Försäljningsraderna ändras inte. Namnen är exempelprodukter i projektets befintliga fiktiva data.

`scripts/rename-sales-finance-products.py` innehåller den stabila namnlistan, uppdaterar endast ProductName och datamanifestets produktfilhash. Den körs även av generatorn före manifestet så att namnen inte återgår vid regenerering. Generatorn har syntaxkontrollerats utan att generera om data eller modell.

Kontroller: alla 30 namn matchar live-modellen via DAX; varje CSV-fil matchar datamanifestet. Oberoende CSV/DAX-kontroll passerar för tre perioder och 96 grupp-/månadskombinationer. Endast produktdimensionen importerades om och modellen beräknades, därefter sparades projektet i Desktop.

Nya Desktop-bilder visar läsbara produktnamn i Ledningsöversiktens och ekonomisidans topplistor samt i transaktionstabellen. Försäljningssidan bildgranskades också; där visas inga produktnamn i huvudvyn. Senaste PBIR-kontroll har inga rapporterade fel men en varning: Microsofts visualContainer-schema 2.13.0 kunde inte hämtas, så schemakontrollen är inte fullständig för de berörda befintliga visualerna. Inga PBIR-komponenter ändrades inom namnbytet. Inget publicerades.
