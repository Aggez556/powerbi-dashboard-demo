"""Budget actuals must cover every transaction day, not only the demo's old 15th."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for p in [root/'powerbi-ledningsrapport/Ledningsrapport.SemanticModel/definition/tables/Budgetscenarier.tmdl',root/'scripts/budget-scenario-model.py']:
 text=p.read_text(encoding='utf-8-sig')
 text=text.replace('VAR _date=[MonthKey]*100+15','VAR _date=[MonthKey]*100+1\n'+ ('\t\t\t' if p.suffix=='.tmdl' else '')+'VAR _last=[MonthKey]*100+DAY(EOMONTH(DATE(_year,MOD([MonthKey],100),1),0))')
 for table in ['Försäljning','Direkta kostnader','Gemensamma kostnader']:
  col=f"'{table}'[Datumnyckel]"
  text=text.replace(f'TREATAS({{_date}},{col})',f'{col}>=_date,{col}<=_last')
 assert 'VAR _date=[MonthKey]*100+15' not in text
 p.write_text(text,encoding='utf-8')
print('Budget actuals now include the full calendar month in source model and generator.')
