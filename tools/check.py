"""校验生成内容与预算；不声称已经核实外部链接或政策有效性。"""
from pathlib import Path
import json
import re
from urllib.parse import unquote
from catalog import CHAPTERS, ITEMS, SOURCES, DATE
from budget import calculate

ROOT=Path(__file__).resolve().parents[1]
errors=[]
def require(ok,message):
    if not ok: errors.append(message)

require(len(set(x['id'] for x in ITEMS))==len(ITEMS),'duplicate item IDs')
require(len(set(c['slug'] for c in CHAPTERS))==len(CHAPTERS),'duplicate chapter slugs')
for x in ITEMS:
    for field in ['id','chapter','title','age','action','money','time','gain','condition','evidence','priority','boundary','checked']:
        require(bool(x.get(field)),f'{x["id"]}: missing {field}')
    for s in x['sources']: require(s in SOURCES,f'{x["id"]}: unknown source {s}')
    if x['evidence'].startswith(('P','G','R','U')):
        require(bool(x['sources']),f'{x["id"]}: factual/guideline claim lacks source')
    require(x['checked']==DATE,f'{x["id"]}: inconsistent date')
for k,s in SOURCES.items():
    require(s['url'].startswith('https://'),f'{k}: non-HTTPS source')
    require(bool(s['status']) and bool(s['scope']),f'{k}: provenance missing')

payload=json.loads((ROOT/'data/guide.json').read_text(encoding='utf-8'))
require(payload['items']==ITEMS,'generated JSON stale; rerun build.py')
reader=(ROOT/'index.html').read_text(encoding='utf-8')
require('/*__DATA__*/' not in reader,'reader payload missing')
match=re.search(r"'use strict';const data=(.*?);\nconst escapeHTML",reader,re.S)
require(bool(match),'reader data not found')
if match: require(json.loads(match[1])['items']==ITEMS,'reader data stale')

for f in ROOT.rglob('*.md'):
    if any(p in {'.git','.cache','outputs','.local'} for p in f.relative_to(ROOT).parts): continue
    text=f.read_text(encoding='utf-8')
    for link in re.findall(r'\]\(([^)]+)\)',text):
        if link.startswith(('https://','http://','mailto:','#')): continue
        dest,_,anchor=link.partition('#')
        target=f.parent/unquote(dest)
        require(target.exists(),f'{f.relative_to(ROOT)}: broken local link {dest}')
        if anchor and target.exists() and target.suffix=='.md':
            require(f'id="{anchor}"' in target.read_text(encoding='utf-8'),f'{f.relative_to(ROOT)}: missing anchor {anchor}')

cities=(ROOT/'docs/cities.md').read_text(encoding='utf-8')
for city in ['南京','苏州','无锡','常州','镇江','南通','扬州','泰州','徐州','连云港','淮安','盐城','宿迁']:
    require(f'| {city} |' in cities,f'missing city {city}')

model=json.loads((ROOT/'data/budget.example.json').read_text(encoding='utf-8'))
result=calculate(model)
require(result['years']==22,'budget duration')
require(result['direct']==443000,'teaching base budget total')
require(sum(r['subtotal'] for r in result['rows'])+model['birth_once']==result['direct'],'budget sum')
model['inflation']=0.02
inflated=calculate(model)
require(inflated['direct']>result['direct'],'inflation not applied')
require(inflated['rows'][-1]['subtotal']>120000*(1.02**18),'university inflation timing')
try:
    bad=dict(model);bad['inflation']=-0.1;calculate(bad)
    errors.append('negative inflation accepted')
except ValueError: pass

if errors:
    for e in errors: print('ERROR:',e)
    raise SystemExit(1)
print(f'PASS: {len(ITEMS)} entries; {len(CHAPTERS)} chapters; {len(SOURCES)} source records; 13 cities; local links; offline payload; budget arithmetic.')
print('External policy validity, site availability and professional review are NOT checked here.')
