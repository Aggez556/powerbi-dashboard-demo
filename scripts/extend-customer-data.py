"""Deterministic customer lifecycle enrichment conserving each financial bucket."""
from pathlib import Path
from collections import defaultdict,deque
from decimal import Decimal
import csv,json,hashlib,re
import numpy as np
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'powerbi-ledningsrapport';DATA=BASE/'data';MODEL=BASE/'Ledningsrapport.SemanticModel/definition'
def read(n):
    with (DATA/f'{n}.csv').open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(n,rows):
    with (DATA/f'{n}.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def alloc(total,weights):
    raw=[Decimal(total)*Decimal(str(w))/sum(Decimal(str(x)) for x in weights) for w in weights];out=[int(v) for v in raw]
    for i in sorted(range(len(out)),key=lambda i:raw[i]-out[i],reverse=True)[:total-sum(out)]:out[i]+=1
    return out
sales=read('Försäljning');costs=read('Direkta kostnader');customers=read('Kunder')
for r in sales:
    for k in ['Datumnyckel','Kundnyckel','Områdesnyckel','Artikelnyckel','Ordernyckel','Nettointäkt']:r[k]=int(r[k])
def period(k):return 'A' if 20251001<=k<=20260930 else 'B' if 20241001<=k<=20250930 else 'other'
def bucket(r):return (r['Datumnyckel'],r['Områdesnyckel'],r['Artikelnyckel'],r['Debitering'],(r['Kundnyckel']-1)%5 if r['Kundnyckel']!=301 else 0)
before=defaultdict(int)
for r in sales:before[bucket(r)]+=r['Nettointäkt']
for r in sales:
    k=r['Kundnyckel'];d=r['Datumnyckel']
    if d>=20251001 and 1<=k<=10:k+=270
    # Link demo credits to an actual existing customer; a credit never creates
    # activity. This also makes historical cohort sums reconcile exactly.
    if k==301:k=11
    r['Kundnyckel']=k
    if r['Områdesnyckel']==1:r['Ordernyckel']=(d//100)*1000+k
prior=defaultdict(int)
for r in sales:
    if period(r['Datumnyckel'])=='B':prior[r['Kundnyckel']]+=r['Nettointäkt']
targets={'A':{},'B':{}}
industry_prior=[45000000,31000000,18000000,15000000,11000000];industry_now=[52000000,36000000,22000000,17500000,12000000]
lost=alloc(4000000,industry_prior);decreased=alloc(18000000,industry_prior);new=alloc(27000000,industry_now);react=alloc(2500000,industry_now)
for ind in range(5):
    keys=lambda lo,hi:[k for k in range(lo,hi+1) if (k-1)%5==ind]
    for cohort,total in [(keys(1,10),lost[ind]),(keys(11,240),industry_prior[ind]-lost[ind])]:
        targets['B'].update(zip(cohort,alloc(total,[prior[k] for k in cohort])))
    down,up=keys(11,125),keys(126,240)
    delta=(industry_now[ind]-new[ind]-react[ind])-(industry_prior[ind]-lost[ind])
    down_base=sum(targets['B'][k] for k in down);up_base=sum(targets['B'][k] for k in up)
    assert down_base>decreased[ind] and delta+decreased[ind]>0
    targets['A'].update(zip(down,alloc(down_base-decreased[ind],[targets['B'][k] for k in down])))
    targets['A'].update(zip(up,alloc(up_base+delta+decreased[ind],[targets['B'][k] for k in up])))
    targets['A'].update(zip(keys(241,275),alloc(new[ind],[1+(k%7)*.05 for k in keys(241,275)])))
    targets['A'].update(zip(keys(276,280),alloc(react[ind],[1]*len(keys(276,280)))))

class Flow:
    def __init__(self,n):self.g=[[] for _ in range(n)]
    def add(self,u,v,c):
        a=[v,c,None];b=[u,0,a];a[2]=b;self.g[u].append(a);self.g[v].append(b);return a
    def run(self,s,t):
        total=0
        while True:
            level=[-1]*len(self.g);level[s]=0;q=deque([s])
            while q:
                u=q.popleft()
                for v,c,_ in self.g[u]:
                    if c and level[v]<0:level[v]=level[u]+1;q.append(v)
            if level[t]<0:return total
            it=[0]*len(self.g)
            def dfs(u,amount):
                if u==t:return amount
                while it[u]<len(self.g[u]):
                    e=self.g[u][it[u]];v,c,rev=e
                    if c and level[v]==level[u]+1:
                        f=dfs(v,min(amount,c))
                        if f:e[1]-=f;rev[1]+=f;return f
                    it[u]+=1
                return 0
            while True:
                f=dfs(s,10**12)
                if not f:break
                total+=f

for p in ['B','A']:
    for ind in range(5):
        rows=[r for r in sales if period(r['Datumnyckel'])==p and bucket(r)[-1]==ind]
        positives=[r for r in rows if r['Nettointäkt']>0];credits=defaultdict(int)
        for r in rows:
            if r['Nettointäkt']<0:credits[r['Kundnyckel']]-=r['Nettointäkt']
        keys=sorted({bucket(r) for r in positives});clients=sorted({r['Kundnyckel'] for r in positives})
        ki={k:i for i,k in enumerate(keys)};ci={k:i for i,k in enumerate(clients)}
        a=np.zeros((len(keys),len(clients)));source={}
        for r in positives:
            i,j=ki[bucket(r)],ci[r['Kundnyckel']];a[i,j]+=r['Nettointäkt'];source[i,j]=r
        row_sums=a.sum(axis=1).astype(np.int64);col_sums=np.array([targets[p][k]+credits[k] for k in clients],dtype=np.int64)
        assert row_sums.sum()==col_sums.sum()
        for iteration in range(3000):
            a*= (row_sums/a.sum(axis=1))[:,None]
            a*= (col_sums/a.sum(axis=0))[None,:]
            if np.max(np.abs(a.sum(axis=1)-row_sums))<.00001:break
        else:raise AssertionError(('raking did not converge',p,ind))
        out=np.floor(a).astype(np.int64);rn=row_sums-out.sum(axis=1);cn=col_sums-out.sum(axis=0)
        n,m=a.shape;s=n+m;t=s+1;flow=Flow(t+1);edges=[]
        for i,v in enumerate(rn):flow.add(s,i,int(v))
        for j,v in enumerate(cn):flow.add(n+j,t,int(v))
        for i,j in source:
            if a[i,j]-out[i,j]>.0000001:edges.append((i,j,flow.add(i,n+j,1)))
        assert flow.run(s,t)==int(rn.sum())
        for i,j,e in edges:out[i,j]+=1-e[1]
        assert np.array_equal(out.sum(axis=1),row_sums) and np.array_equal(out.sum(axis=0),col_sums)
        for (i,j),r in source.items():
            old=r['Nettointäkt'];r['Nettointäkt']=int(out[i,j]);assert r['Nettointäkt']>0
            if r['Debitering']=='Timdebiterat':r['Debiterade timmar']=f"{Decimal(r['Debiterade timmar'])*Decimal(r['Nettointäkt'])/Decimal(old):.4f}"
after=defaultdict(int)
for r in sales:after[bucket(r)]+=r['Nettointäkt']
assert before==after,'Financial bucket totals changed'
# Allocate only attributable costs, retaining explicitly unallocated personnel.
weights=defaultdict(lambda:defaultdict(int))
for r in sales:weights[(r['Datumnyckel'],r['Områdesnyckel'],r['Artikelnyckel'])][r['Kundnyckel']]+=r['Nettointäkt']
aggregated=defaultdict(int)
for r in costs:aggregated[(int(r['Datumnyckel']),int(r['Områdesnyckel']),int(r['Artikelnyckel']),r['Kostnadstyp'])]+=int(r['Belopp'])
new_cost=[]
for (d,a,article,kind),total in aggregated.items():
    pairs=[(k,max(v,0)) for k,v in sorted(weights[d,a,article].items()) if v>0]
    if 'fördelad' in kind.lower():pairs=[(0,1)]
    for (k,_),amount in zip(pairs,alloc(total,[v for _,v in pairs])):
        if amount:new_cost.append(dict(Datumnyckel=d,Områdesnyckel=a,Kostnadstyp=kind,Belopp=amount,Artikelnyckel=article,Kundnyckel=k))
first={};last={}
for r in sales:
    if r['Nettointäkt']>0:
        k=r['Kundnyckel'];first[k]=min(first.get(k,r['Datumnyckel']),r['Datumnyckel']);last[k]=max(last.get(k,0),r['Datumnyckel'])
names={11:'Bistro Strand',241:'Kökspartner Nord',276:'Hotell Björken',126:'Kontor Väster',1:'Restaurang Kajen'}
for r in customers:
    k=int(r['Kundnyckel']);r['Kund']='Ej kundfördelat' if k==0 else names.get(k,f'Kundföretag {k:03d}')
    r['Första köp']=str(20200615 if 276<=k<=280 else first.get(k,0))
    r['Historiskt köp före data']='Ja' if 276<=k<=280 else 'Nej'
if not any(int(r['Kundnyckel'])==0 for r in customers):customers.append(dict(Kundnyckel=0,Kund='Ej kundfördelat',Ort='',Kundbransch='',**{'Första köp':'0','Historiskt köp före data':'Nej'}))
write('Försäljning',sales);write('Direkta kostnader',new_cost);write('Kunder',customers)
jobs=read('Uppdrag')
for r in jobs:
    if int(r['Datumnyckel'])>=20251001 and 1<=int(r['Kundnyckel'])<=10:r['Kundnyckel']=int(r['Kundnyckel'])+270
write('Uppdrag',jobs)
statuses=[{'Status':n,'Ordning':i} for i,n in enumerate(['Alla','Befintliga','Helt nya','Återaktiverade','Förlorade'])]
groups=[{'Kundgrupp':n,'Ordning':i} for i,n in enumerate(['Befintliga','Helt nya','Återaktiverade'])]
write('Kundstatusval',statuses);write('Kundgrupper',groups)
write('Kundbassteg',[{'Steg':n,'Ordning':i} for i,n in enumerate(['Föregående','Helt nya','Återaktiverade','Förlorade'])])
write('Kundintäktssteg',[{'Steg':n,'Ordning':i} for i,n in enumerate(['Föregående','Förlorade','Minskade köp','Ökade köp','Helt nya','Återaktiverade'])])
for table,cols in {'Kundstatusval':[('Status','string'),('Ordning','int64')],'Kundgrupper':[('Kundgrupp','string'),('Ordning','int64')],'Kundbassteg':[('Steg','string'),('Ordning','int64')],'Kundintäktssteg':[('Steg','string'),('Ordning','int64')]}.items():
    text=f'/// Frikopplad presentationsaxel för kundanalys.\ntable {table}\n'
    for name,typ in cols:
        text+=f"\n\tcolumn '{name}'\n\t\tdataType: {typ}\n\t\tsourceColumn: {name}\n\t\tsummarizeBy: none\n"
        if typ=='int64':text+='\t\tisHidden\n'
        if name in ['Status','Kundgrupp','Steg']:text+='\t\tsortByColumn: Ordning\n'
    casts=', '.join('{"'+n+'", '+('Int64.Type' if t=='int64' else 'type text')+'}' for n,t in cols)
    text+=f'\n\tpartition {table} = m\n\t\tmode: import\n\t\tsource =\n\t\t\tlet\n\t\t\t\tSource = Csv.Document(File.Contents(DataFolder & "/{table}.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n\t\t\t\tHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n\t\t\t\tTyped = Table.TransformColumnTypes(Headers, {{{casts}}}, "en-US")\n\t\t\tin\n\t\t\t\tTyped\n'
    target=MODEL/'tables'/f'{table}.tmdl'
    if not target.exists():target.write_text(text,encoding='utf-8')
    p=MODEL/'model.tmdl';s=p.read_text(encoding='utf-8-sig')
    if f'ref table {table}' not in s:p.write_text(s+f'\nref table {table}\n',encoding='utf-8')
for table,cols in {'Kunder':[('Första köp','int64'),('Historiskt köp före data','string')],'Direkta kostnader':[('Kundnyckel','int64')]}.items():
    p=MODEL/'tables'/f'{table}.tmdl';s=p.read_text(encoding='utf-8-sig')
    for n,typ in cols:
        if not re.search(r"(?m)^\tcolumn '?"+n+r"'?\s*$",s):s+=f"\n\tcolumn '{n}'\n\t\tdataType: {typ}\n\t\tsourceColumn: {n}\n\t\tsummarizeBy: none\n\t\tisHidden\n"
        if '"'+n+'"' not in s:s=s.replace('}}, "en-US")','}, {"'+n+'", '+('Int64.Type' if typ=='int64' else 'type text')+'}}, "en-US")')
    p.write_text(s,encoding='utf-8')
p=MODEL/'relationships.tmdl';s=p.read_text(encoding='utf-8-sig')
if "relationship 'Kundanalys direkta kostnader'" not in s:p.write_text(s+"\nrelationship 'Kundanalys direkta kostnader'\n\tfromColumn: 'Direkta kostnader'.Kundnyckel\n\ttoColumn: Kunder.Kundnyckel\n\tfromCardinality: many\n\ttoCardinality: one\n\tcrossFilteringBehavior: oneDirection\n",encoding='utf-8')
for temporary in [DATA/'Kundbryggsteg.csv',MODEL/'tables/Kundbryggsteg.tmdl']:
    if temporary.exists():temporary.unlink()
p=MODEL/'model.tmdl';p.write_text(p.read_text(encoding='utf-8-sig').replace('\nref table Kundbryggsteg\n','\n'),encoding='utf-8')
manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8'))
manifest['rows'].pop('Kundbryggsteg',None);manifest['sha256'].pop('Kundbryggsteg',None)
for n in ['Försäljning','Direkta kostnader','Kunder','Uppdrag','Kundstatusval','Kundgrupper','Kundbassteg','Kundintäktssteg']:
    manifest['rows'][n]=len(read(n));manifest['sha256'][n]=hashlib.sha256((DATA/f'{n}.csv').read_bytes()).hexdigest()
manifest['customerEnrichment']='scripts/extend-customer-data.py; integer balanced allocation preserving each date/area/article/billing/industry total; attributable costs only, unallocated personnel retained.'
(DATA/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary={'status':'passed','financialBucketsPreserved':len(before),'salesRows':len(sales),'costRows':len(new_cost),'method':'IPF customer targets with exact integer network-flow rounding, preserving detailed financial buckets','firstPurchaseHistory':'Five reactivated customers explicitly purchased before data history, June 2020','cohorts':{'continuing':230,'new':35,'reactivated':5,'lost':10},'revenueTargets':targets}
(BASE/'validation/customer-enrichment.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='revenueTargets'}))
