from pathlib import Path
p=Path(__file__).resolve().parents[1]/'powerbi-ledningsrapport/validation/assignment-live-check.dax'
row='ROW("Case","{case}","Jobs",[Uppdrag utförda],"PreviousJobs",[Uppdrag utförda föregående],"Hours",[Utfall timmar],"Available",[Utfall kapacitet],"Margin",[Utfall marginal],"Booked",[Plan bokat],"Capacity",[Plan kapacitet],"Free",[Plan ledigt],"Over",[Plan överbeläggning])'
cases=[]
for mode,end in [('R12','September 2026'),('Helår','2025'),('Helår','2024'),('Månad','September 2026')]:
 table={'R12':'R12val','Helår':'Helårsval','Månad':'Månadsval'}[mode]
 filters=f'TREATAS({{"{mode}"}},\'Periodtyp\'[Periodtyp]),TREATAS({{"{end}"}},{chr(39)+table+chr(39)}[Period])'
 cases.append('CALCULATETABLE('+row.format(case=mode+' '+end)+','+filters+')')
base='TREATAS({"R12"},\'Periodtyp\'[Periodtyp]),TREATAS({"September 2026"},\'R12val\'[Period])'
for name,key in [('Teknisk service',2),('Bemanning',3)]:cases.append('CALCULATETABLE('+row.format(case=name)+','+base+f",TREATAS({{{key}}},'Uppdragsområden'[Områdesnyckel]))")
for name in ['Tekniker Nord','Tekniker Syd','Diskpersonal','Städpersonal']:
 cases.append('CALCULATETABLE('+row.format(case=name)+','+base+f',TREATAS({{"{name}"}},\'Resursval\'[Resursgrupp]))')
cases.append('CALCULATETABLE('+row.format(case='Invalid group fallback')+','+base+',TREATAS({2},\'Uppdragsområden\'[Områdesnyckel]),TREATAS({"Diskpersonal"},\'Resursval\'[Resursgrupp]))')
cases.append('CALCULATETABLE('+row.format(case='Historical cross-filter')+','+base+',TREATAS({20240115},\'Datum\'[Datumnyckel]),TREATAS({DATE(2025,1,1)},\'Trendaxel\'[Månadsstart]))')
s='EVALUATE UNION('+',\n'.join(cases)+') ORDER BY [Case]\n'
s+='\nEVALUATE CALCULATETABLE(SUMMARIZECOLUMNS(\'Resurser\'[Resursgrupp],\'Planveckor\'[Vecka],"Booked",[Plan bokat],"Capacity",[Plan kapacitet],"Free",[Plan ledigt],"Over",[Plan överbeläggning],"Rate",[Plan beläggning]),'+base+') ORDER BY \'Resurser\'[Resursgrupp],\'Planveckor\'[Vecka]\n'
s+='\nEVALUATE CALCULATETABLE(SUMMARIZECOLUMNS(\'Uppdragsregister\'[UppdragID],\'Uppdragsregister\'[Uppdrag],"Visible",[Uppdrag synligt],"WholeHours",[Uppdrag hela timmar],"Risk",[Uppdrag risk],"Forecast",[Uppdrag prognos],"Customer",[Uppdrag kund]),'+base+') ORDER BY \'Uppdragsregister\'[UppdragID]\n'
p.write_text(s,encoding='utf-8')
print('Prepared actual DAX checks for periods, areas, resources, invalid selection and historical cross-filter isolation.')
