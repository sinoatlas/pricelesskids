# 首版校验记录

版本1.0.0，校验日期2026-10-10。下面记录真正执行的检查，未执行的项目不标通过。

| 检查 | 结果 | 范围 |
| --- | --- | --- |
| 生成章节、README、完整书、JSON和离线HTML | 通过 | 93条 / 16章 / 52项来源与线索 |
| 字段完整、条目编号唯一、章节编号唯一、来源映射 | 通过 | 本地结构一致性 |
| Markdown本地文件链接与明确编号锚点 | 通过 | 不代表原站HTTP可达 |
| 13市核查卡存在 | 通过 | 不代表每市全部规则已核 |
| 教学预算分阶段加总、22年年限、增长率时序 | 通过 | 基准443000元，2%及4%仅为敏感性输入 |
| Python代码语法编译 | 通过 | build/catalog/check/budget/package/publish |
| 离线JavaScript执行 | 通过 | 本地VM模拟DOM，初始93条、关键词、章节、待核筛选、收藏保存与仅收藏 |
| ZIP CRC与文件清单 | 通过 | 发布包公共文件；缓存和真实家庭数据未纳入 |
| 上传器dry-run | 通过 | 只列白名单，不认证、不联网、不提交 |
| 上传器真实GitHub端到端 | **未执行** | 缺可用认证连接；网页登录不自动提供API写权限 |
| 浏览器实际渲染与手机视觉验收 | **未完成** | 浏览器工具超时及URL识别限制；不把VM测试当视觉验收 |
| 全来源实时可达性 | **未完成** | 部分原站403、412、超时或缓存失败，台账标明 |
| 医学/法律/教育专业人员逐条审稿 | **未完成** | 无机构认证或专业签字 |

## 复现本地检查

```console
python tools/build.py
python tools/check.py
python tools/budget.py
python -m py_compile tools/build.py tools/catalog.py tools/check.py tools/budget.py tools/package.py tools/publish.py
python tools/publish.py --dry-run
python tools/package.py
```

校验不是发布证明。真正的远端验证需提交链接、提交SHA、默认分支状态和文件列表；只有网页目录或上传器验证记录能说明实际上传结果。
