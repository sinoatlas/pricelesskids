"""使用 Python 标准库生成 Markdown、结构化 JSON 和离线检索页。"""
from pathlib import Path
import json
import html
import re
from catalog import CHAPTERS, ITEMS, SOURCES, DATE

ROOT = Path(__file__).resolve().parents[1]
def write(path, text):
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding='utf-8', newline='\n')

def md_item(x):
    fields = [('年龄 / 场景',x['age']),('怎么做',x['action']),('金钱成本',x['money']),
              ('时间与精力',x['time']),('主要收益',x['gain']),('适用条件',x['condition']),
              ('依据类型',x['evidence']),('行动优先级',x['priority']+'（编辑判断）'),
              ('边界 / 容易误解处',x['boundary']),('核验日期',x['checked'])]
    rows = '\n'.join(f'| {a} | {b.replace(chr(10)," ").replace("|","／")} |' for a,b in fields)
    refs = '\n'.join(f'- [{s}: {SOURCES[s]["title"]}]({SOURCES[s]["url"]}) — {SOURCES[s]["status"]}；适用范围：{SOURCES[s]["scope"]}。' for s in x['sources'])
    return f'### {x["id"]} · {x["title"]}\n\n| 字段 | 内容 |\n| --- | --- |\n{rows}\n\n'+(refs or '依据：本项目原创决策建议，无直接效果研究；不包装为循证结论。')+'\n\n'

def build():
    for c in CHAPTERS:
        body = ''.join(f'<a id="{x["id"]}"></a>\n\n'+md_item(x) for x in ITEMS if x['chapter']==c['slug'])
        write(f'book/{c["slug"]}.md',f'# {c["title"]}\n\n{c["intro"]}\n\n[返回目录](../README.md) · [核验方法](../docs/methodology.md) · [来源台账](../docs/sources.md)\n\n{body}')
    write('data/guide.json',json.dumps(dict(version='1.0.0',checked=DATE,chapters=CHAPTERS,items=ITEMS,sources=SOURCES),ensure_ascii=False,indent=2)+'\n')
    source_text = '# 来源与核验台账\n\n核验日期：'+DATE+'。来源台账共 '+str(len(SOURCES))+' 项；包括政策、指南、论文旁证、媒体线索与核查入口，不能都算成完整核验的循证证据。\n\n'
    source_text += '正文读取方式来自检索工具；检索正文不等于成功打开原站。未能读取的附件、当年执行细则与统计全文均明确标记。状态只描述本次核查，不保证原页面日后可访问。\n\n'
    for s in SOURCES.values():
        source_text += f'## {s["id"]} · {s["title"]}\n\n- 发布者：{s["publisher"]}\n- 文件 / 页面日期：{s["published"]}\n- 原始链接：[{s["title"]}]({s["url"]})\n- 适用范围：{s["scope"]}\n- 核验状态：{s["status"]}\n- 本次核查要点：{s["note"]}\n- 核验日期：{s["checked"]}\n\n'
    write('docs/sources.md',source_text)
    write('docs/entry-index.md','# 条目索引\n\n'+ '\n'.join(f'- [{x["id"]} · {x["title"]}](../book/{x["chapter"]}.md#{x["id"]})' for x in ITEMS)+'\n')
    # GitHub的自动标题锚点对标点处理会变化；完整书使用明确的HTML id。
    alltext = '# 高性价比养娃指南 · 江苏版\n\n完整阅读版；核验日期 '+DATE+'。先读[方法](methodology.md)与[13市差异](cities.md)。\n\n'
    for c in CHAPTERS:
        alltext += f'## {c["title"]}\n\n{c["intro"]}\n\n'
        for x in ITEMS:
            if x['chapter']==c['slug']:
                alltext += f'<a id="{x["id"]}"></a>\n\n'+md_item(x)
    write('docs/complete-guide.md',alltext)
    # Source paths in md_item only contain external links, so complete text is portable.
    nav = '\n'.join(f'| {i+1:02} | [{c["title"]}](book/{c["slug"]}.md) | {sum(x["chapter"]==c["slug"] for x in ITEMS)} |' for i,c in enumerate(CHAPTERS))
    readme = f'''# 高性价比养娃指南 · 江苏版

把钱、时间和精力花在健康、安全、稳定照护、学习能力与孩子的选择机会。覆盖出生到大学毕业；常见四年本科为约0—22岁，其他学制自行调整。

**{len(ITEMS)}条建议 · {len(CHAPTERS)}个主题 · 13市差异索引 · {len(SOURCES)}项来源与线索记录**

核验日期：{DATE} · 版本：1.0.0 · 本项目为独立原创资料整理，未经政府或医学机构认证。没有承诺所有政策、费用、县区及病情均已穷尽核验。

[完整阅读](docs/complete-guide.md) · [13市索引](docs/cities.md) · [家庭预算](docs/budget.md) · [办事清单](docs/checklists.md) · [离线检索页](index.html) · [来源与核验](docs/sources.md) · [证据方法](docs/methodology.md)

在线检索页部署后入口：[sinoatlas.github.io/pricelesskids](https://sinoatlas.github.io/pricelesskids/)。该链接是**预期部署地址**，只有仓库启用 Pages 并成功部署后才可用。本地直接打开 `index.html` 可离线搜索，不上传搜索词和收藏。

## 先做这几件事

1. 出生后尽早完成医保登记与到账，核对出生当年和次年的区别。
2. 核实育儿补贴与个税扣除资格：补贴是现金，扣除是税前扣除。
3. 安全睡眠、乘车约束、水边看护和必要就医优先于用品升级。
4. 用好社区儿保、免疫规划和学校公共资源，适龄女孩询问新版HPV免费项目。
5. 入学、转学、选科、志愿按当年属地文件办理，不买“包录取”。

## 怎么用

每条写明做法、金钱、时间、收益、适用条件、依据类型、优先级与来源。按当前年龄挑一两条即可；不是家长任务考核表。优先级是编辑判断，P（政策）、G（指南）、R（研究）、J（判断）、U（待核）是依据类型，不是一条从强到弱的单维排行榜。

政策的有效性、研究的效果与家庭选择的适配性是三件不同的事。带出处不代表整个条目每句都来自该出处；P+J、G+J明确表示建议部分是编辑组织方法。待核线索不用于作确定性资格判断。

## 目录

| 章 | 主题 | 条目数 |
| --- | --- | --- |
{nav}

## 江苏地方化范围

13市均有核查卡。部分卡使用已读官方正文，部分只有县区示例或媒体线索，具体状态见城市索引。居民医保保费、幼儿园收费、学区、招生资格和中考规则没有被写成全省统一标准。2026招生日期已过者仅作当年例子，不外推2027。大学所在地不在江苏时，学校及就医地规则另核。

## 预算与维护

预算是**自拟教学输入**，不是物价调查、江苏均价或未来支出承诺。拆分住房、付费照护、机会成本、补贴、贷款和消费，避免重复计算。见[预算模型](docs/budget.md)。

修改 `tools/catalog.py` 的原创目录，再运行：

```console
python tools/build.py
python tools/check.py
python tools/budget.py
```

Python 3.10及以上；使用标准库，无需安装第三方依赖。校验检查条目、来源映射、本地链接、重复编号和预算逻辑，不替代专业内容复核。

## 参考项目与许可

编排方式参考 eternity4719 的[《高性价比人生指南》](https://github.com/eternity4719/HowToLiveBetter)：按问题分章、标明成本收益、适用条件和出处。正文重新调研撰写，没有复制原书段落；这不是原项目官方江苏分册。

本项目原创文字与结构化内容采用[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，代码采用MIT，详见[许可范围](LICENSE.md)与[致谢](docs/attribution.md)。第三方原文、机构标志及链接目标不受本项目许可覆盖。

欢迎按[贡献指南](CONTRIBUTING.md)提交带官方来源的纠错，尤其补充待核城市和县区。请勿在Issue或提交中包含儿童姓名、证件、住址、诊断、学校班级等私人信息。
'''
    write('README.md',readme)
    payload=json.dumps(dict(items=ITEMS,chapters=CHAPTERS,sources=SOURCES),ensure_ascii=False).replace('<','\\u003c').replace('&','\\u0026')
    template=(ROOT/'tools/reader.html').read_text(encoding='utf-8')
    write('index.html',template.replace('/*__DATA__*/',payload))
    print(f'Built {len(ITEMS)} items / {len(CHAPTERS)} chapters / {len(SOURCES)} source records.')

if __name__=='__main__':
    build()
