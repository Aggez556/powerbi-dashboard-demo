# Ledningsrapport – genomförandespecifikation

Användaren har uttryckligen godkänt genomförandet enligt bifogad prompt och referensbild samt ett separat nytt lokalt projekt från grunden. Senaste styrning: färger, typsnitt och liknande ska inspireras av befintliga delar av codex-labb. Detta dokument bevarar den redan godkända omfattningen; inget ytterligare godkännande krävs för lokala projektfiler. Publicering ingår inte.

## Låst omfattning

Exakt Start och Ledningsöversikt. Start inspireras av befintligt Sales Finance. Fem planerade områden visas; endast Ledningsöversikt är aktiv. Svenskt språk. Native Power BI-visualer och DAX, inte en bild av en rapport. Komplett reproducerbar lokal demodata från januari 2023 till september 2026. Alla kontrollbelopp används direkt och skalas inte igen. Standardperiod R12 september 2026.

Designavvägning enligt senaste instruktion: referensbildens layout kombineras med den befintliga mappens Aubeco-palett och Segoe UI. Canvas 1920 × 1200 följer referensbildens ungefärliga 1,6:1-proportioner och passar i FitToPage. Datadiagram använder navy/emerald; orange markerar vald månad och portalens betoning. Ingen annan organisations logotyp används.

```yaml
Design Brief:
  generated_by: powerbi-report-cli
  contract_version: 1
  mode: greenfield
  phase: implementation_authorized
  design_identity:
    tone: Lugn svensk ledningsrapport med mörkblå struktur och ljusa sandtoner
    signature: Sales Finance-inspirerad portal och referensbildens sex KPI-kort ovanför fyra vita analysytor
  font_strategy: Segoe UI för data och Segoe UI Semibold för hierarki
  theme_file: Ledningsrapport.Report/StaticResources/RegisteredResources/LedningsrapportTheme.json
  color_map:
    Nettoomsättning: '#0F3163'
    Teknisk service: '#0F3163'
    Bemanning: '#007956'
    Rörelsemarginal: '#007956'
    Positiv förändring: '#007956'
    Negativ förändring: '#B42318'
    Vald månad: '#9B570B'
  pages:
    - name: Start
      archetype: Navigation Portal
      layout_contract:
        canvas: {width: 1920, height: 1200}
        grid:
          regions:
            header: {x: 64, y: 56, width: 1792, height: 304}
            navigation: {x: 64, y: 408, width: 1792, height: 436}
            footer: {x: 64, y: 972, width: 1792, height: 136}
        placements:
          page_title: {type: textbox, text: En gemensam bild av verksamheten, box: [64, 196, 1700, 80]}
          navigation_cards: {count: 5, box: [64, 408, 1792, 436], active: Ledningsöversikt}
        space_audit: {unintentional_overlap: false, planned_overlap: text_and_button_inside_navigation_panels}
    - name: Ledningsöversikt
      archetype: Executive Summary
      variant: KPI Strip
      layout_contract:
        canvas: {width: 1920, height: 1200}
        grid:
          regions:
            navigation: {x: 0, y: 0, width: 272, height: 1200}
            header: {x: 304, y: 16, width: 752, height: 128}
            filters: {x: 1080, y: 8, width: 784, height: 96}
            kpis: {x: 288, y: 160, width: 1604, height: 184}
            analysis: {x: 288, y: 360, width: 1612, height: 816}
        placements:
          page_title: {type: textbox, text: Ledningsöversikt, box: [304, 16, 780, 64]}
          period_type: {type: bookmark_buttons, box: [1080, 40, 372, 56]}
          relevant_period: {type: dropdown_slicer, box: [1496, 8, 368, 96]}
          kpi_cards: {count: 6, box: [288, 160, 1604, 184], basis: model_measures}
          revenue_margin: {type: lineStackedColumnComboChart, box: [312, 432, 750, 320]}
          completed_jobs: {type: columnChart, box: [1126, 432, 750, 320]}
          areas: {type: pivotTable, box: [312, 872, 750, 220]}
          result_bridge: {type: waterfallChart, box: [1126, 904, 750, 244]}
        space_audit: {unintentional_overlap: false, planned_overlap: panels_and_bookmark_control_variants}
```

Acceptance: exact standard controls; valid R12/Helår/Månad comparisons; period-correct budget and unique customer counts; month-mode trend history and marker; Start navigation; inactive future areas; PBIR/TMDL validation; actual Desktop import, DAX execution and captured screenshots if the local host supports them. Do not equate file validation with rendered validation.
