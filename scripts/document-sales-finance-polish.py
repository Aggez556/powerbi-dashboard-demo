from pathlib import Path
root=Path(__file__).resolve().parents[1]/'powerbi-sales-finance'
for name in ['README.md','report-spec.md']:
    p=root/name
    s=p.read_text(encoding='utf-8-sig')
    for a,b in [('Executive Overview','Ledningsöversikt'),('Finance & Profitability','Ekonomi och lönsamhet'),('Sales Analytics','Försäljningsanalys'),('Transactions','Transaktioner')]:
        s=s.replace(a,b)
    p.write_text(s,encoding='utf-8')
with (root/'validation/README.md').open('a',encoding='utf-8') as f:
    f.write('\n## Svenska och layoutjusteringar\n\nRapportens sidnamn, rubriker och navigationsknappar har översatts till svenska. Årsjämförelse visas som Årsförändring. Fyra lika breda startsideskort, centrerade SVG-ikoner och knappar med korrigerade innermarginaler. Sid-ID och navigation är bevarade. Modellen och datan har inte ändrats i detta steg. PBIR-validering har inga fel; en tillfällig schemahämtningsvarning gäller den oförändrade PBIP-startfilen. Senaste rapportlayouten har lästs in i Desktop. Skärmbildsgranskning pågår.\n')
