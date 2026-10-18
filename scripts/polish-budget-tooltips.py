from pathlib import Path
p=Path(__file__).with_name('budget-statement-spec.cjs')
s=p.read_text(encoding='utf-8')
s=s.replace("datum.Label+' · '+datum.Group+' · '+datum.Metric+': '+datum.Text+(datum.Slot===3?' · Positivt är bättre än jämförelsen; marginaler visas i procentenheter.':'')", "{'Post':datum.Label,'Period':datum.Group,'Jämförelse':datum.Metric,'Värde':datum.Text}")
s=s.replace("datum.Label+' · '+datum.Group+': '+datum.VarianceText+' · Positivt är bättre än jämförelsen. Marginaler i procentenheter; nollreferens visas som streck.'", "{'Post':datum.Label,'Period':datum.Group,'Avvikelse':datum.VarianceText,'Tolkning':'Plus = bättre, minus = sämre'}")
p.write_text(s,encoding='utf-8')
