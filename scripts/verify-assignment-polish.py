from pathlib import Path
import json
BASE=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport'
result=json.loads((BASE/'validation/assignment-polish-result.json').read_text(encoding='utf-8-sig'))['resultSets']
missing=0
for r in result[0]:
 if r['Uppdragsregister[Status]']=='Avslutat':assert r['[Risk]']==0
 if r['[Forecast]'] is None:
  missing+=1;assert r['[Text]']=='—'
  if (r['[Hours]'] or 0)<=(r['[Planned]'] or 0):assert r['[Risk]']==0
assert [r['[Status]'] for r in result[1]]==['Alla','Pågående','Avslutade','Behöver uppföljning']
assert any('110' in r['[Text]'] for r in result[2])
summary=dict(status='passed',source='Actual Desktop DAX',assignmentsChecked=len(result[0]),missingForecastsChecked=missing,missingForecastsDoNotImplyMarginRisk=True,statusOrderVerified=True,overbookingPercentagesPreserved=True)
(BASE/'validation/assignment-polish-verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary))
