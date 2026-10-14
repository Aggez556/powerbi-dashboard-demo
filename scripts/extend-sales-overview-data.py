"""Deterministic category/industry/order/hour enrichment, conserving all month/area totals."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import csv,json,hashlib,re

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'powerbi-ledningsrapport';DATA=BASE/'data';MODEL=BASE/'Ledningsrapport.SemanticModel/definition'
def read(n):
    with (DATA/(n+'.csv')).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(n,rows):
    with (DATA/(n+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def allocate(total,weights):
    weights=[Decimal(str(w)) for w in weights];den=sum(weights)
    if total==0:return [0]*len(weights)
    assert den>0 and total>=0
    raw=[Decimal(total)*w/den for w in weights];out=[int(v) for v in raw]
    for i in sorted(range(len(raw)),key=lambda i:raw[i]-out[i],reverse=True)[:total-sum(out)]:out[i]+=1
    return out
def transport(rows,cols):
    assert sum(rows)==sum(cols),(sum(rows),sum(cols))
    remaining=cols[:];out=[]
    for total in rows:
        values=allocate(total,remaining) if sum(remaining) else [0]*len(cols)
        assert all(v<=r for v,r in zip(values,remaining))
        remaining=[r-v for r,v in zip(remaining,values)];out.append(values)
    assert sum(remaining)==0
    return out

cats=[('Maskiner',1,35000000,30000000,7000000),('Rengöringsprodukter',1,30000000,25000000,10800000),('Förbrukningsmaterial',1,20000000,18000000,6000000),('Service',2,12000000,9000000,4320000),('Reparationer',2,10000000,8000000,2300000),('Installationer',2,8000000,6000000,2680000),('Diskpersonal',3,14000000,14000000,1680000),('Städpersonal',3,10500000,10000000,1260000)]
industries=['Restaurang','Hotell','Catering','Kontor','Livsmedel']
industry=lambda key:0 if key==301 else (key-1)%5
sales=read('Försäljning');costs=read('Direkta kostnader');customers=read('Kunder')
groups=defaultdict(lambda:{'net':0,'credit':0,'buyers':set(),'cost':0,'types':defaultdict(int)})
for r in sales:
    g=groups[(int(r['Datumnyckel'])//100,int(r['Områdesnyckel']))];v=int(r['Nettointäkt']);g['net']+=v
    if v>0:g['buyers'].add(int(r['Kundnyckel']))
    else:g['credit']-=v
for r in costs:
    g=groups[(int(r['Datumnyckel'])//100,int(r['Områdesnyckel']))];g['cost']+=int(r['Belopp']);g['types'][r['Kostnadstyp']]+=int(r['Belopp'])
# The requested previous category mix is 73/23/24 Mkr; the older demo used
# 73/25/22. Transfer 2 Mkr and the matching direct cost, preserving each
# month's company revenue/result and every area's previous gross profit.
previous_keys=sorted(k for k in groups if 202410<=k[0]<=202509 and k[1]==2)
previous_service=sum(groups[k]['net'] for k in previous_keys)
assert previous_service in [23000000,25000000],previous_service
if previous_service==23000000:previous_keys=[]
for k,transfer in zip(previous_keys,allocate(2000000 if previous_keys else 0,[groups[k]['net'] for k in previous_keys])):
    service=groups[k];staff=groups[(k[0],3)]
    service['net']-=transfer;staff['net']+=transfer
    service['cost']-=transfer;staff['cost']+=transfer
    parts=allocate(transfer,list(service['types'].values()))
    for t,part in zip(service['types'],parts):service['types'][t]-=part
    staff['types']['Direkt leveranspersonal']+=transfer
before={k:(v['net'],v['cost'],sorted(v['buyers'])) for k,v in groups.items()}
periods=defaultdict(list)
for k in sorted(groups):
    ym=k[0];period='current' if 202510<=ym<=202609 else 'previous' if 202410<=ym<=202509 else str(ym)
    periods[period].append(k)
new_sales=[];new_costs=[]
for period,keys in periods.items():
    net=sum(groups[k]['net'] for k in keys);credits=sum(groups[k]['credit'] for k in keys)
    targets=[52000000,36000000,22000000,17500000,12000000] if period=='current' else [45000000,31000000,18000000,15000000,11000000] if period=='previous' else allocate(net,[52,36,22,17.5,12])
    positive_targets=targets[:];positive_targets[0]+=credits
    industry_alloc=transport([groups[k]['net']+groups[k]['credit'] for k in keys],positive_targets)
    category_net={};category_cost={}
    for area in (1,2,3):
        area_keys=[k for k in keys if k[1]==area];indices=[i for i,c in enumerate(cats) if c[1]==area]
        area_net=sum(groups[k]['net'] for k in area_keys);area_cost=sum(groups[k]['cost'] for k in area_keys)
        cat_net=[cats[i][2 if period=='current' else 3] for i in indices] if period in ['current','previous'] else allocate(area_net,[cats[i][2] for i in indices])
        cat_gp=[cats[i][4] for i in indices] if period=='current' else allocate(area_net-area_cost,[cats[i][3] for i in indices]) if period=='previous' else allocate(area_net-area_cost,[cats[i][4] for i in indices])
        cat_cost=[r-g for r,g in zip(cat_net,cat_gp)]
        net_matrix=transport([groups[k]['net'] for k in area_keys],cat_net)
        cost_matrix=transport([groups[k]['cost'] for k in area_keys],cat_cost)
        for j,k in enumerate(area_keys):category_net[k]=dict(zip(indices,net_matrix[j]));category_cost[k]=dict(zip(indices,cost_matrix[j]))
    for ki,k in enumerate(keys):
        ym,area=k;g=groups[k];indices=list(category_net[k]);positive_cats=[category_net[k][i]+(g['credit'] if ci==0 else 0) for ci,i in enumerate(indices)]
        joint=transport(industry_alloc[ki],positive_cats)
        datekey=ym*100+15
        def add_sale(customer,ci,amount,billing,hours,article):
            # All delivered product rows for one customer/month share an order identity.
            order=ym*1000+customer if area==1 else 0
            new_sales.append({'Fakturarad':len(new_sales)+1,'Datumnyckel':datekey,'Kundnyckel':customer,'Områdesnyckel':area,'Nettointäkt':amount,'Typ':'Försäljning' if amount>0 else 'Kreditnota','Artikelnyckel':(ci+1)*10+article,'Ordernyckel':order,'Debitering':billing,'Debiterade timmar':f'{hours:.4f}'})
        for ind in range(5):
            buyers=sorted(c for c in g['buyers'] if industry(c)==ind);assert buyers
            for j,ci in enumerate(indices):
                values=allocate(joint[ind][j],[1+(c%11)*.08 for c in buyers])
                for customer,amount in zip(buyers,values):
                    for article,part in enumerate(allocate(amount,[55,45]),1):
                        if area==1:add_sale(customer,ci,part,'Produkt',Decimal(0),article)
                        else:
                            labor,material,fixed=allocate(part,[80,12,8] if area==2 else [96,0,4])
                            rate=Decimal(740+ci*20 if area==2 else 340+ci*5)
                            if labor:add_sale(customer,ci,labor,'Timdebiterat',Decimal(labor)/rate,article)
                            if material:add_sale(customer,ci,material,'Material',Decimal(0),article)
                            if fixed:add_sale(customer,ci,fixed,'Fastpris',Decimal(0),article)
        ci=indices[0]
        rate=Decimal(740+ci*20 if area==2 else 340+ci*5)
        add_sale(301,ci,-g['credit'],'Produkt' if area==1 else 'Timdebiterat',Decimal(0) if area==1 else -Decimal(g['credit'])/rate,1)
        types=list(g['types']);matrix=transport([g['types'][t] for t in types],[category_cost[k][i] for i in indices])
        for ti,t in enumerate(types):
            for j,ci in enumerate(indices):
                for article,amount in enumerate(allocate(matrix[ti][j],[55,45]),1):
                    new_costs.append({'Datumnyckel':datekey,'Områdesnyckel':area,'Kostnadstyp':t,'Belopp':amount,'Artikelnyckel':(ci+1)*10+article})

for r in customers:r['Kundbransch']=industries[industry(int(r['Kundnyckel']))]
products=[]
for i,(cat,area,*_) in enumerate(cats):
    for article in (1,2):products.append({'Artikelnyckel':(i+1)*10+article,'Kategori':cat,'Artikel':cat+(' – standard' if article==1 else ' – utökad'),'Kategoriordning':i+1,'Område':['Produktförsäljning','Teknisk service','Bemanning'][area-1],'Områdesordning':area})
series=[{'Serie':n,'Typ':'Område','Nyckel':i+1,'Ordning':i} for i,n in enumerate(['Produktförsäljning','Teknisk service','Bemanning'])]+[{'Serie':c[0],'Typ':'Kategori','Nyckel':i+1,'Ordning':i+3} for i,c in enumerate(cats)]
area_options=[{'Verksamhetsområde':n,'Områdesval':i} for i,n in enumerate(['Alla områden','Produktförsäljning','Teknisk service','Bemanning'])]
write('Försäljning',new_sales);write('Direkta kostnader',new_costs);write('Kunder',customers);write('Artiklar',products);write('Försäljningsserie',series);write('Områdesval',area_options)
after=defaultdict(lambda:[0,0,set()])
for r in new_sales:
    k=(r['Datumnyckel']//100,r['Områdesnyckel']);after[k][0]+=r['Nettointäkt']
    if r['Nettointäkt']>0:after[k][2].add(r['Kundnyckel'])
for r in new_costs:after[(r['Datumnyckel']//100,r['Områdesnyckel'])][1]+=r['Belopp']
assert all((v[0],v[1],sorted(v[2]))==before[k] for k,v in after.items())

def add_columns(table,columns):
    p=MODEL/'tables'/f'{table}.tmdl';s=p.read_text(encoding='utf-8-sig')
    for n,kind in columns:
        if re.search(r"(?m)^\tcolumn '?"+re.escape(n)+r"'?\s*$",s):continue
        s+=f"\n\t/// Underlag för försäljningsanalys.\n\tcolumn '{n}'\n\t\tdataType: {kind}\n\t\tsourceColumn: {n}\n\t\tsummarizeBy: none\n"
        if n not in ['Kundbransch','Debitering']:s+='\t\tisHidden\n'
    missing=[(n,kind) for n,kind in columns if '"'+n+'"' not in s]
    if missing:
        extra=', '.join('{"'+n+'", '+('Int64.Type' if kind=='int64' else 'Currency.Type' if kind=='decimal' else 'type text')+'}' for n,kind in missing)
        s=s.replace('}}, "en-US")','}, '+extra+'}, "en-US")')
    p.write_text(s,encoding='utf-8')
add_columns('Försäljning',[('Artikelnyckel','int64'),('Ordernyckel','int64'),('Debitering','string'),('Debiterade timmar','decimal')])
add_columns('Direkta kostnader',[('Artikelnyckel','int64')]);add_columns('Kunder',[('Kundbransch','string')])
for table,cols in {'Artiklar':[('Artikelnyckel','int64'),('Kategori','string'),('Artikel','string'),('Kategoriordning','int64'),('Område','string'),('Områdesordning','int64')],'Försäljningsserie':[('Serie','string'),('Typ','string'),('Nyckel','int64'),('Ordning','int64')],'Områdesval':[('Verksamhetsområde','string'),('Områdesval','int64')]}.items():
    s=f"/// Reproducerbart analysunderlag.\ntable '{table}'\n"
    for n,kind in cols:
        s+=f"\n\tcolumn '{n}'\n\t\tdataType: {kind}\n\t\tsourceColumn: {n}\n\t\tsummarizeBy: none\n"
        if kind=='int64' or n=='Typ':s+='\t\tisHidden\n'
        if n=='Kategori':s+="\t\tsortByColumn: Kategoriordning\n"
        if n=='Område':s+="\t\tsortByColumn: Områdesordning\n"
        if n=='Serie':s+="\t\tsortByColumn: Ordning\n"
        if n=='Verksamhetsområde':s+="\t\tsortByColumn: Områdesval\n"
    cast=', '.join('{"'+n+'", '+('Int64.Type' if t=='int64' else 'type text')+'}' for n,t in cols)
    s+=f'\n\tpartition \'{table}\' = m\n\t\tmode: import\n\t\tsource =\n\t\t\tlet\n\t\t\t\tSource = Csv.Document(File.Contents(DataFolder & "/{table}.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n\t\t\t\tHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n\t\t\t\tTyped = Table.TransformColumnTypes(Headers, {{{cast}}}, "en-US")\n\t\t\tin\n\t\t\t\tTyped\n'
    # Existing Desktop metadata can contain translations and lineage bindings.
    # The CSV schema is stable; retain its table definition on data-only rebuilds.
    table_path=MODEL/'tables'/f'{table}.tmdl'
    if not table_path.exists():table_path.write_text(s,encoding='utf-8')
    p=MODEL/'model.tmdl';text=p.read_text(encoding='utf-8-sig')
    if not re.search(r"ref table '?"+table+r"'?\s*$",text,re.M):text+=f"\nref table '{table}'\n";p.write_text(text,encoding='utf-8')
p=MODEL/'relationships.tmdl';text=p.read_text(encoding='utf-8-sig')
for fact in ['Försäljning','Direkta kostnader']:
    name='Sälj '+fact+' artikel'
    if name not in text:text+=f"\nrelationship '{name}'\n\tfromColumn: '{fact}'.Artikelnyckel\n\ttoColumn: Artiklar.Artikelnyckel\n\tfromCardinality: many\n\ttoCardinality: one\n\tcrossFilteringBehavior: oneDirection\n"
p.write_text(text,encoding='utf-8')
manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8'))
for n in ['Försäljning','Direkta kostnader','Kunder','Artiklar','Försäljningsserie','Områdesval']:
    manifest['rows'][n]=len(read(n));manifest['sha256'][n]=hashlib.sha256((DATA/(n+'.csv')).read_bytes()).hexdigest()
manifest['enrichment']='scripts/extend-sales-overview-data.py; integer transportation allocations, preserving each month/area net revenue, direct cost, positive-customer set and all prior overview controls.'
(DATA/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
checks={'status':'passed','monthAreaGroupsPreservedAfterDocumentedPriorMixAdjustment':len(before),'priorMixAdjustment':'Previous R12 service/staff revenue and matching direct cost transferred 2 Mkr, to reconcile requested category totals 73/23/24 Mkr. Company monthly revenue and gross profit by area remain unchanged.','salesRows':len(new_sales),'costRows':len(new_costs),'categories':[],'industries':[]}
for ci,c in enumerate(cats):
    amount=sum(r['Nettointäkt'] for r in new_sales if 202510<=r['Datumnyckel']//100<=202609 and r['Artikelnyckel']//10==ci+1)
    cost=sum(r['Belopp'] for r in new_costs if 202510<=r['Datumnyckel']//100<=202609 and r['Artikelnyckel']//10==ci+1)
    assert amount==c[2] and amount-cost==c[4],(c,amount,cost)
    checks['categories'].append({'name':c[0],'revenue':amount,'grossProfit':amount-cost})
for ind,n in enumerate(industries):
    amounts=[sum(r['Nettointäkt'] for r in new_sales if lo<=r['Datumnyckel']//100<=hi and industry(r['Kundnyckel'])==ind) for lo,hi in [(202510,202609),(202410,202509)]]
    assert amounts==[[52000000,36000000,22000000,17500000,12000000][ind],[45000000,31000000,18000000,15000000,11000000][ind]]
    checks['industries'].append({'name':n,'revenue':amounts[0],'previous':amounts[1]})
(BASE/'validation/sales-data-enrichment.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'passed','preservedMonthAreas':len(before),'salesRows':len(new_sales),'categoryControls':8,'industryControls':5}))
if 'Första köp' in (MODEL/'tables/Kunder.tmdl').read_text(encoding='utf-8-sig'):
    import subprocess,sys
    subprocess.run([sys.executable,str(ROOT/'scripts/extend-customer-data.py')],check=True)
