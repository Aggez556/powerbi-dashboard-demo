# Demodatans timpriser

`scripts/vary-hourly-rates.py` anpassar endast fakturaradernas debiterade timmar. Intäkter, kostnader, datum, kunder och artiklar behålls. Timpriset räknas fortfarande som timdebiterad nettointäkt dividerad med nettotimmar, inklusive krediteringar.

Månadspriserna ändras med områdets bruttomarginal jämfört med samma månad föregående år. Fallande marginal ger lägre pris; stabil eller stigande marginal ger högre pris. Priserna varierar dessutom mellan fakturarader. Detta är ett scenario för demodata, ingen generell ekonomisk regel om sambandet mellan marginal och pris.

Kontrollen omfattar 92 månads-/områdeskombinationer samt helår 2024, 2025 och R12 september 2026 för båda tjänsteområdena. Detaljer finns i `validation/hourly-rate-checks.json`. För andra perioder och filtreringar beräknas timpriset som ett vägt genomsnitt av deras faktiska urval.

Godkänd tid på uppdragssidan är en separat datakälla och ändras inte av denna justering av fakturerade timmar. Efter källändringen behöver försäljningstabellen uppdateras i Desktop och rapporten sparas för att importcachen ska finnas kvar nästa gång projektet öppnas.
