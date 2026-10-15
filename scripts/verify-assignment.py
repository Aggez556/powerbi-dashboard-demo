"""Independent checks against persisted real Desktop DAX results."""
from pathlib import Path
from datetime import date
from collections import defaultdict
import csv,json,math
BASE=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport';DATA=BASE/'data';OUT=BASE/'validation'
def read(n):return list(csv.DictReader((DATA/(n+'.csv')).open(encoding='utf-8-sig')))
live=json.loads((OUT/'assignment-live-result.json').read_text(encoding='utf-8-sig'))['resultSets']
cases={r['[Case]']:r for r in live[0]}
expected={'R12 September 2026':[6800,8000,1280,80],'Helår 2025':[6800,8000,1280,80],'Helår 2024':[6800,8000,1280,80],'Månad September 2026':[6800,8000,1280,80],'Historical cross-filter':[6800,8000,1280,80],'Teknisk service':[2960,3200,320,80],'Bemanning':[3840,4800,960,0],'Tekniker Nord':[1600,1600,80,80],'Tekniker Syd':[1360,1600,240,0],'Diskpersonal':[2400,2800,400,0],'Städpersonal':[1440,2000,560,0],'Invalid group fallback':[2960,3200,320,80]}
for case,values in expected.items():
 for field,value in zip(['Booked','Capacity','Free','Over'],values):assert math.isclose(cases[case]['['+field+']'],value,abs_tol=1e-7),(case,field)
assert [cases['R12 September 2026'][f] for f in ['[Jobs]','[PreviousJobs]']]==[960,840]
assert cases['Teknisk service']['[Jobs]']==640 and cases['Bemanning']['[Jobs]']==320
for r in live[1]:
 group=r['Resurser[Resursgrupp]'];week=int(r['Planveckor[Vecka]'][1:]);i=['Tekniker Nord','Tekniker Syd','Diskpersonal','Städpersonal'].index(group)
 booked=[220 if week<45 else 180,180 if week<45 else 160,300,180][i];cap=[200,200,350,250][i]
 assert math.isclose(r['[Booked]'],booked,abs_tol=1e-7) and math.isclose(r['[Capacity]'],cap,abs_tol=1e-7)
 assert math.isclose(r['[Rate]'],booked/cap,abs_tol=1e-9)
registry={int(r['UppdragID']):r for r in read('Uppdragsregister')};hours=defaultdict(float)
timesheets=read('Utförd tid')
for r in timesheets:hours[int(r['UppdragID'])]+=float(r['Timmar'])
period_bounds={'Helår 2025':(20250101,20251231),'Helår 2024':(20240101,20241231),'R12 September 2026':(20251001,20260930),'Månad September 2026':(20260901,20260930)}
for case,(start,end) in period_bounds.items():
 expected_hours=sum(float(r['Timmar']) for r in timesheets if start<=int(r['Datumnyckel'])<=end)
 assert math.isclose(cases[case]['[Hours]'],expected_hours,abs_tol=1e-7),(case,cases[case]['[Hours]'],expected_hours)
visible=0
for r in live[2]:
 jid=r['Uppdragsregister[UppdragID]'];j=registry[jid]
 overlap=j['Startdatum']<='2026-09-30' and (not j['Slutdatum'] or j['Slutdatum']>='2025-10-01')
 assert (r['[Visible]']==1)==overlap
 assert math.isclose(r['[WholeHours]'] or 0,hours[jid],abs_tol=1e-9)
 if overlap:visible+=1
 rel=(BASE/'Ledningsrapport.SemanticModel/definition/relationships.tmdl').read_text(encoding='utf-8-sig')
assert 'Planbokningar' in rel and "fromColumn: 'Planbokningar'.'Datumnyckel'" not in rel
meta=json.loads((BASE/'LedningsrapportUtanScroll.Report/definition/pages/pages.json').read_text())
assert len(meta['pageOrder'])==7
summary=dict(status='passed',scope='Actual Desktop DAX compared with independent CSV calculations; UI interactions not yet reviewed',periodAreaResourceCases=len(cases),weeklyGroupCells=len(live[1]),assignmentRowsChecked=len(live[2]),visibleAssignments=visible,standardJobs=960,previousJobs=840,standardHours=cases['R12 September 2026']['[Hours]'],availableHours=cases['R12 September 2026']['[Available]'],planBooked=6800,planCapacity=8000,planFree=1280,planOver=80)
interaction=json.loads((OUT/'assignment-interaction-result.json').read_text(encoding='utf-8-sig'))['resultSets']
status={r['Uppdragsstatusval[Urval]']:r for r in interaction[0]}
assert status['Alla']['[Visible]']==status['Pågående']['[Visible]']+status['Avslutade']['[Visible]']==visible
assert all(r['[Booked]']==6800 and r['[Jobs]']==960 for r in status.values())
assert status['Behöver uppföljning']['[Visible]']>0
assert len(interaction[1])==240
assert math.isclose(sum(r['[Booked]'] for r in interaction[1]),6800,abs_tol=1e-7)
assert math.isclose(sum(r['[Free]'] for r in interaction[1]),1280,abs_tol=1e-7)
assert math.isclose(sum(r['[Over]'] for r in interaction[1]),80,abs_tol=1e-7)
assert len(interaction[2])==12 and sum(r['[Selected]'] is not None for r in interaction[2])==1
assert all(math.isclose(r['[Target]'],.82,abs_tol=1e-9) for r in interaction[2])
old=interaction[3][0];assert [old['['+k+']'] for k in ['Revenue','GrossProfit','EBIT','Customers','Jobs']]==[139500000,36040000,8000000,270,960]
summary.update(statusFiltersVerified=True,employeeWeekCells=240,monthContextMonths=12,selectedMonthMarkers=1,previousReportTotalsPreserved=True)
(OUT/'assignment-verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary))
