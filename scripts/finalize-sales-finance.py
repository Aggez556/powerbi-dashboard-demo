from pathlib import Path
p = Path(__file__).with_name('build-sales-finance.cjs')
s = p.read_text(encoding='utf-8')
s = s.replace('Månadsutveckling · aktuellt år och föregående år', 'Månadsutveckling')
s = s.replace('Omsättning per land / kategori', 'Omsättning per marknad')
s = s.replace('],30,i===2?', '],20,i===2?')
s = s.replace('visualContainerObjects:{title:', 'visualContainerObjects:{subTitle:[{properties:{show:lit(false)}}],title:')
p.write_text(s, encoding='utf-8')
