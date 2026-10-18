"""Validate actual Desktop DAX output against independently checked CSV results."""
from pathlib import Path
import json,math
base=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport/validation'
live=json.loads((base/'customer-live-result.json').read_text(encoding='utf-8-sig'))['resultSets']
independent=json.loads((base/'customer-independent-checks.json').read_text(encoding='utf-8'))
ref=live[0][0]
source=independent['reference']
expected=dict(zip(['Aktiva','Tidigare','Fortsatta','Helt nya','Återaktiverade','Förlorade'],[source[k] for k in ['active','previous','continuing','new','reactivated','lost']]))
expected.update({'Intäkt':source['revenue'],'Tidigare intäkt':source['previousRevenue'],'Fortsatta intäkt':source['cohortRevenue'][0],'Nya intäkt':source['cohortRevenue'][1],'Återaktiverade intäkt':source['cohortRevenue'][2],'Förlorad intäkt':-source['bridge'][1],'Minskning':source['bridge'][2],'Ökning':source['bridge'][3],'Ledning intäkt':source['revenue'],'Ledning bryggfel':0})
for k,v in expected.items():assert math.isclose(ref['['+k+']'],v,abs_tol=.00001),(k,ref)
for k,v in {'Logo churn':source['logoChurn'],'Revenue churn':source['revenueChurn'],'Andel nya':source['newRevenueShare']}.items():assert math.isclose(ref['['+k+']'],v)
groups={}
for row in live[2]:groups[row['Kundgrupper[Kundgrupp]']]=groups.get(row['Kundgrupper[Kundgrupp]'],0)+row['[Mkr]']
expected_trend_rows=sum(amount!=0 for month in independent['reference']['monthly'].values() for amount in month)
assert len(live[2])==expected_trend_rows
assert all(math.isclose(groups[k],v/1000000) for k,v in zip(['Befintliga','Helt nya','Återaktiverade'],source['cohortRevenue']))
for row in live[1]:
    for field in ['[Aktiva]','[Nya]','[Förlorade]']:
        assert row[field] is None or row[field]==int(row[field]),(field,row)
    industry=row['Kunder[Kundbransch]']
    if not industry:continue
    case=next(x['result'] for x in independent['scenarios'] if x['mode']=='R12 september' and x['industry']==industry)
    assert row['[Aktiva]']==case['active'] and row['[Intäkt]']==case['revenue']
for row in live[3]:
    case=next(x['result'] for x in independent['scenarios'] if x['industry']=='Alla' and x['mode']==('Månad september, churn R12' if row['[Period]'].startswith('Månad') else row['[Period]']))
    assert row['[Aktiva]']==case['active'] and row['[Intäkt]']==case['revenue']
    assert math.isclose(row['[Churn]'],case['revenueChurn'])
assert len(live[4])==10 and all(x['[Status]']=='Förlorad' and x['[Synlig]']==1 for x in live[4])
result={'status':'passed','source':'Actual refreshed Desktop DAX, compared with independent persisted CSV calculations','reference':expected,'trendRows':len(live[2]),'trendGroupsMkr':groups,'lostCustomerRows':10,'checks':['all reference KPIs','financial bridge amounts','five industry cases','full years 2024/2025','monthly customer analysis uses R12','cohort trend sums','lost-only follow-up filter','overview reconciliation']}
(base/'customer-live-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'passed','source':result['source'],'trendRows':len(live[2]),'trendGroupsMkr':groups,'lostCustomerRows':10}))
