"""教学预算；运行 python tools/budget.py [家庭JSON路径]。不联网、不处理证件。"""
import json
import sys
from pathlib import Path
from copy import deepcopy
ROOT = Path(__file__).resolve().parents[1]
KEYS = {'food','supplies','clothing_transport','health','education_care','optional'}
def calculate(model):
    rows=[]
    rate=model['inflation']
    if not isinstance(rate,(int,float)) or not 0<=rate<=1:
        raise ValueError('inflation must be between 0 and 1')
    total=model['birth_once']
    end=0
    for stage in model['stages']:
        assert stage['start_age']==end, 'age intervals must be contiguous'
        assert isinstance(stage['years'],int) and stage['years']>0
        assert set(stage['annual'])==KEYS
        assert all(isinstance(v,(int,float)) and v>=0 for v in stage['annual'].values())
        yearly=sum(stage['annual'].values())
        sub=sum(yearly*(1+rate)**age for age in range(end,end+stage['years']))
        rows.append(dict(name=stage['name'],annual=yearly,years=stage['years'],subtotal=round(sub,2)))
        total+=sub
        end+=stage['years']
    assert all(isinstance(model[k],(int,float)) and model[k]>=0 for k in ['birth_once','annual_housing_increment','annual_opportunity_cost','benefits_total'])
    extra=sum((model['annual_housing_increment']+model['annual_opportunity_cost'])*(1+rate)**age for age in range(end))
    return dict(years=end,rows=rows,direct=round(total,2),extras=round(extra,2),benefits=model['benefits_total'],net=round(total+extra-model['benefits_total'],2))

def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'data/budget.example.json'
    model=json.loads(path.read_text(encoding='utf-8-sig'))
    result=calculate(model)
    # Windows默认终端编码也能输出中文，管道时由运行者设置PYTHONIOENCODING。
    print('Teaching inputs; NOT a Jiangsu price survey. Currency: CNY.')
    for x in result['rows']:
        print(f'{x["name"]}: annual={x["annual"]:,.0f}, years={x["years"]}, subtotal={x["subtotal"]:,.2f}')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},ensure_ascii=False))
    for rate in [0,0.02,0.04]:
        scenario=deepcopy(model);scenario['inflation']=rate
        print(f'Assumed annual growth {rate:.0%}: {calculate(scenario)["net"]:,.2f} (sensitivity, not forecast)')
if __name__=='__main__': main()
