# Rapportspecifikation: AubecoHandel

Användaren har uttryckligen beställt ett komplett lokalt testprojekt. Syftet är att demonstrera en läsbar handelsrapport med Aubecos profil, reproducerbara fiktiva data och granskningsbara projektfiler. Antagen målgrupp är försäljningsansvarig och produktansvarig. Ingen publicering ingår.

```yaml
project: AubecoHandel
format: PBIP + TMDL + PBIR
storage: Import
data: local CSV, fixed seed 20261006
canvas: { width: 1920, height: 1080 }
theme_source: themes/aubeco-powerbi.json
design_guide: docs/aubeco-powerbi-designguide.md
fonts: [Segoe UI, Segoe UI Semibold]
default_year: 2025
pages:
  - name: Försäljningsöversikt
    question: Hur utvecklas försäljning och lönsamhet, och vilka kunder är störst?
    filters: [Datum.År, Produkter.Kategori]
    cards: [Omsättning, Bruttovinst, Bruttomarginal, Antal order, Tillväxt mot föregående år]
    card_row: { x: 32, y: 184, height: 152, card_width: 352, gap: 24 }
    charts:
      - type: lineChart
        fields: [Datum.År–månad, Försäljning.Omsättning]
        box: [32, 368, 1088, 640]
        sort: chronological
      - type: clusteredBarChart
        fields: [Kunder.Kund, Försäljning.Omsättning]
        box: [1144, 368, 744, 640]
        top: 10
        sort: revenue_descending
  - name: Produktanalys
    question: Vilka kategorier och produkter driver omsättning och marginal?
    filters: [Datum.År, Produkter.Kategori]
    charts:
      - type: clusteredBarChart
        fields: [Produkter.Kategori, Försäljning.Omsättning]
        box: [32, 184, 904, 320]
      - type: clusteredBarChart
        fields: [Produkter.Kategori, Försäljning.Bruttomarginal]
        box: [960, 184, 928, 320]
      - type: clusteredBarChart
        fields: [Produkter.Produkt, Försäljning.Omsättning]
        box: [32, 528, 904, 480]
        top: 10
      - type: tableEx
        fields: [Kategori, Produkt, Omsättning, Kostnad, Bruttovinst, Bruttomarginal]
        box: [960, 528, 928, 480]
        rows: all_products_with_scroll
navigation: native_page_tabs
slicer_sync: false
```

Modellkontrakt: Försäljning har 10 000 rader, Datum 731, Kunder 100, Produkter 30. Tre aktiva enkelriktade relationer filtrerar Försäljning från dimensionerna. Datumtabellen är markerad. Tekniska nycklar döljs. Mått och visningsfält är svenska, med SEK, procent och heltal. Ingen artificiell föregåendeårsbas skapas för 2024.

Taste används genom profilanknytning, konsekvent hierarki och återhållsam form. Installerad Taste är uttryckligen avsedd för webbgränssnitt och utesluter dashboards; Microsofts Power BI-instruktioner styr därför visualtyper, bindningar och rapportstruktur. Webbanimationer och dekorativa webbkomponenter införs inte.

Teknisk granskning omfattar statiska kontroller och en senare Desktop-kontroll av import, DAX, filter, Top 10 och rendering. Se powerbi/validation/README.md för faktiskt genomförda kontroller.
