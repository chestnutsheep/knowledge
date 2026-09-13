---
tags: [SOP, 机构观点, 流程, 技能包]
type: "SOP"
updated: 2026-09-08
---

# SOP：研报库「采集 → PDF 正文抽取 → 概念聚类速览」闭环（技能包）

> 用途：把「肆 • 机构观点」下的券商研报，从「只有链接和时间线」升级成「可读正文 + 按赛道聚合的机构共识/分歧驾驶舱」。
> 适用：本知识库。脚本都在真实 vault 的 `肆 • 机构观点/`（带 `_` 前缀），幂等、可重复跑。
> 本文件即**技能包**：任何采集/整理任务结束后，照第 2 节的默认闭环走即可，无需用户再单独提"按内容整理"。

## 0. 何时用本 SOP
- 跑完 `fetch_reports.py` 采集（定时任务 16:30 自动跑，或手动补采）。
- 用户要求"把研报正文抽出来 / 补核心观点 / 做概念卡 / 看机构共识分歧"。
- 新增研报概念、或 notebook 新建了主题板块需要挂接。
- 全量回填历史研报正文（数百篇 PDF 下载）。

## 1. 基础设施清单（脚本与职责，当前状态均为已落地可用）

| 脚本 | 方向 | 职责 | 当前状态 |
|------|------|------|----------|
| `fetch_reports.py` | 0 采集 | 东方财富主源拉研报，写 `研报_<日期>_<序号>.md` 笔记 + 刷新 `00-研报时间线.md`；frontmatter 已含 `concept/object/industry/rating/title/pdfUrl` | 可用，自动探测 vault |
| `_extract_pdf.py` | **1 正文** | 下 PDF → pdfplumber 抽文本 → 规则抽取「核心观点/盈利预测/投资建议/风险因素」写回笔记 | 已修：vault 探测、代理、◼兜底、风险标题扩展、OCR 噪声过滤 |
| `_gen_obsidian.py` | **3 概念卡** | 扫 frontmatter 重建元数据 → 生成 MOC + 概念卡片 + Canvas + 逆索引 + 共识综述 + 笔记交叉引用回填 | 已修：`_scan_meta` 含 `title`、`build_consensus` 注入 `## 共识综述`、MOC 日期动态 |
| `README-研报采集器.md` | 0 | `fetch_reports.py` 使用说明 | 参考 |

辅助/历史（勿在新流程调用）：`_extract_meta.py`（已弃用，能力被 fetch 的 classify 覆盖）、`_meta.json`（已弃用，生成器改扫 frontmatter）、`_build_concept_map.py` / `_backfill_notes.py` / `_migrate_*.py`（旧迁移产物）。

## 2. 默认闭环三步（内容整理是默认期望，采集后必须自动跟）

> 关键点：**步骤 2+3 是用户的默认期望，不是可选项**。任何采集/整理任务结束后，必须自动跟进，不要等用户单独提"按内容整理"。

**环境前置（每次跑脚本前确认）**：
- 代理在线：`pgrep -f clash-verge` 在则 OK；不在则 `nohup /usr/bin/clash-verge >/tmp/clash-verge.log 2>&1 &`（监听 `127.0.0.1:7897`）。
- 可选 env：`JRJ_API_KEY`（金融界补充源）、`DAYS_BACK`（回看天数，默认 7）、`VAULT_DIR`（vault 根，默认自动探测 `/home/AI/笔记/知识库`）。

**步骤 1 — 采集**
```bash
cd "/home/AI/笔记/知识库/肆 • 机构观点"
python3 fetch_reports.py
```
- 看到 `[INFO] 模式: 真实拉取` = 真数据；`DRY_RUN` = key 未配，仅重建 timeline。
- 错误码 42902=配额耗尽、40101=key 失效，需提示用户。

**步骤 2 — 抽 PDF 正文（方向 1）**
```bash
# 日常增量（跳过已有 ## 核心观点 的笔记，只补新笔记）：前台即可
python3 _extract_pdf.py all
# 一次性全量回填（数百篇 PDF 下载，前台会被静默杀）→ 必须后台：
nohup python3 _extract_pdf.py all > /tmp/backfill.log 2>&1 &
```
- 规则式抽取（按研报结构，非 LLM，**不编造**）；空值属正常降级（结构异常研报核心观点可能为空）。

**步骤 3 — 生成概念卡 + 共识综述（方向 3）**
```bash
python3 _gen_obsidian.py
```
产出：`00-研报概念速览.md`（主驾驶舱）+ `概念卡片/<概念>.md`（15+ 张，含 `## 共识综述`）+ `研报概念架构.canvas` + `研报逆检索索引.md` + 每篇笔记的 `## 知识库交叉引用` 回填。

## 3. 方向 1 详解：PDF 正文抽取（`_extract_pdf.py`）

**抽取字段与策略（稳健、可降级）**
- `核心观点`：截取正文要点块（见兜底）；去广告/免责/页眉页脚噪声。
- `盈利预测`：正则抓"预计归母净利润 X/Y/Z 亿元（对应 PE A/B/C 倍）"，只在"盈利预测"段提取，避免误抓实际利润。
- `投资评级`：首页"优于大市(维持)"或正文"维持"xxx"评级"。
- `投资建议`：抓"投资建议："段，过滤免责声明里出现的同名段。
- `风险因素`：抓风险提示段到锚点前。
- 抽不到的字段 → 不生成该章节（条件渲染，不制造空占位）。

**运行模式**
- `python3 _extract_pdf.py <stem> <pdfUrl>`：测试单篇（不写可先 `cached` 看质量）。
- `python3 _extract_pdf.py all [--limit=N] [--force]`：批量，幂等跳过已有 `## 核心观点`；`--force` 重抽。
- `python3 _extract_pdf.py cached [--limit=N] [--dry-run]`：只重解析本地 `_pdf_cache/*.pdf`，修复历史污染，不下载。
- `python3 _extract_pdf.py sanitize [--dry-run]`：只净化既有自动章节/ frontmatter，不重抽。

**PDF 下载与代理**
- `download_pdf()` 用 `urllib.request.ProxyHandler({"http":proxy,"https":proxy})`，proxy 默认 `http://127.0.0.1:7897`（取 `HTTPS_PROXY`/`HTTP_PROXY` env，否则默认）。
- **⚠️ 不能给 `opener.open(req, context=...)` 传 `context` 参数**（`OpenerDirector.open` 不支持，会抛 TypeError）。直连分支才用 `context=ssl.CERT_NONE`。

**抽取规则与兜底（已踩坑并固化）**
- 核心观点无"核心观点"标题的研报：兜底抓「首个要点符号 `◼//•` 段 → 估值/评级/风险锚」之间的正文（含紧邻导语段）。
- 风险标题扩到：`风险提示/风险因素/评级面临的主要风险/主要风险/投资风险/风险分析`。
- 截断锚（`FINANCE_ANCHORS`/`SECTION_END`/`DISCLAIMER_RE`）：`年结日/人民币百万/百万元/Table/盈利预测和财务指标/资产负债表/相关研究报告/免责声明` 等——碰到即停，不吞财务表。
- OCR/损坏碎片过滤（`_is_noise_line`）：`投Ta资bl摘e_F要chinaSimple`、`Table/Footnote/china`、孤字 `•/-/—`、纯数字表行、连续日期串、侧栏行情词（市场数据/收盘价/总市值/股价走势…）。

**已知局限**
- 规则式（非 LLM），少数结构异常研报核心观点可能为空 → 正常降级，不编造。
- 双栏排版已做侧栏裁剪（`_page_text` 按 x 坐标剔除右侧市场数据栏），复杂表页降级用 `extract_text(layout=True)`。

## 4. 方向 3 详解：概念聚类与共识综述（`_gen_obsidian.py`）

**元数据来源**：`build_consensus` / 卡片生成依赖 `_scan_meta()` 直接扫 `研报_*.md` 的 frontmatter（**不依赖已废弃的 `_meta.json`**）。字段：concept/declareDate→date/org/object/industry/rating/**title**。

**`build_consensus(concept, items)` 逻辑（规则聚合，不依赖 LLM）**
- 评级分布：`Counter` 按基础评级（去"（维持）"）统计，most_common 列出。
- 机构立场判定：bull=买入/增持/强烈推荐/推荐/优于大市；neutral=中性/持有/谨慎推荐；bear=减持/卖出。
  - 全无评级 → "多数中报点评未给明确评级，立场以业绩描述为主"。
  - bear==0 且 neutral==0 → "机构高度共识看多"。
  - bull==0 且 neutral==0 → "机构一致谨慎"。
  - bull ≥ neutral+bear → "整体偏多，但存在分歧（看多 X vs 中性/谨慎 Y）"。
  - 否则 → "分歧明显（看多 X vs 中性/谨慎 Y）"。
- 高关注标的：按 `object`（去代码后缀）覆盖频次取 Top6。
- 近期观点脉络：按 date 倒序取前 8 篇，列「日期｜机构｜标题」。
- 注入每张概念卡为 `## 共识综述` 章节（重跑不覆盖用户手动写的版本）。

**逆检索映射（核心维护点）**：`CONCEPT_TO_BOARD` 字典（概念 → notebook 已有板块列表）。新增研报概念或 notebook 新建主题板块时，**只改这一个字典**，重跑步骤 3。当前已挂接 15 概念到贰杂学/伍基本信息池/零导览/叁国家政策等板块。板块路径不存在时退回父目录或提示新建（如 `消费/出海` 的 `东鹏饮料` 用 `exists()` 探测）。

**产出物**
- `00-研报概念速览.md`：Dashboard 静态预览 + Dataview **活清单**（新增笔记自动聚合，无需重跑）+ 卡片网格 + 时间线入口 + 逆检索总索引 + Canvas 入口。MOC 头部日期动态为当前。
- `概念卡片/<概念名>.md`：文件名 `/`→`·`；含共识综述 + 研报清单表 + 逆检索板块。
- `研报概念架构.canvas`：研报→概念→notebook 板块可视化。
- `研报逆检索索引.md`：从 notebook 板块反查相关研报概念。
- 每篇笔记 `## 知识库交叉引用`：回填归属概念卡 + 逆检索板块链接（孤岛变网状）。

## 5. 关键坑（必读，已踩过并修复）

1. **真实 vault 路径** `/home/AI/笔记/知识库`（旧 `/home/AI/Obsidian/知识库` 已不存在）。三脚本均用 `_resolve_vault()` 自动探测，**勿硬编码路径**。
2. **代理 `OpenerDirector` 不能传 `context` 参数** → TypeError。见第 3 节。
3. **前台长任务会被静默杀**：一次性全量回填（数百篇 PDF 下载）必须 `nohup ... &` 后台跑，勿前台执行。后台 PID 用 `pgrep -f "_extract_pdf.py"` 看；进度看 `/tmp/backfill.log`。
4. **`_meta.json` 已废弃**：生成器改扫 frontmatter（`_scan_meta`），勿再依赖。
5. **`build_consensus` 需要 `title` 字段**：已在 `_scan_meta` 补齐，勿删（否则共识综述的"近期观点脉络"为空）。
6. **双 vault 拓扑**（见第 6 节）：确认你在真实 vault 跑脚本，别跑 workspace 的旧镜像副本。
7. 概念名含 `/` 不能做文件名 → `fname()` 转 `·`。链接用 `[[完整文件名]]` 最稳。

## 6. ⚠️ 双 vault 拓扑（运行环境，务必先读）

- **真实数据 vault**：`/home/AI/笔记/知识库/肆 • 机构观点` —— 脚本（`_extract_pdf.py`/`_gen_obsidian.py` 的**已修复版**）、`研报_<日期>_<序号>.md` 笔记、概念卡片均在此。Obsidian 打开的就是这个。
- **Agent 工作区（平行旧副本）**：`/home/AI/scapegoat_data/notebooks/知识库/肆 • 机构观点` —— 可能是旧快照（`_gen_obsidian.py` 旧版、缺 `_extract_pdf.py`、旧命名 `2026-08-31_*.md`）。

**规则**：
- 实际跑脚本 / 看产出，一律用真实 vault 路径（`cd "/home/AI/笔记/知识库/肆 • 机构观点"` 或设 `VAULT_DIR`）。
- 编辑脚本前先确认读的是真实 vault 的版本（带 `_resolve_vault`、带 `build_consensus` 的是新版）。
- 本 SOP 在真实 vault 与 workspace 各存一份，保持一致；以真实 vault 为准。

## 7. 日常维护与扩展

- **新增研报概念**：在 `fetch_reports.py` 的 classify 里归类；若需挂 notebook 板块，在 `_gen_obsidian.py` 的 `CONCEPT_TO_BOARD` 加映射；重跑步骤 3。
- **新建 notebook 主题板块**：建好后把路径加进 `CONCEPT_TO_BOARD` 对应概念；重跑步骤 3。
- **全量回填历史正文**：8 月及更早约 2200 篇尚未抓正文（日常只覆盖新增+9月批次）→ 后台 `nohup python3 _extract_pdf.py all > /tmp/backfill.log 2>&1 &`。
- **文案去 AI 味**：MOC/卡片导读段用口语化短句（已固化在 `_gen_obsidian.py` 字符串），改文案只动该文件。

## 8. 命令速查

```bash
# 环境
pgrep -f clash-verge || nohup /usr/bin/clash-verge >/tmp/clash-verge.log 2>&1 &

# 默认闭环
cd "/home/AI/笔记/知识库/肆 • 机构观点"
python3 fetch_reports.py                 # 1 采集
python3 _extract_pdf.py all              # 2 抽正文（增量）
nohup python3 _extract_pdf.py all > /tmp/backfill.log 2>&1 &   # 2 全量回填（后台）
python3 _gen_obsidian.py                 # 3 概念卡+共识综述

# 单篇/质量自检（不写盘先看）
python3 _extract_pdf.py cached --limit=3 --dry-run
python3 _extract_pdf.py <stem> <pdfUrl>  # 单篇实测

# 进度
tail -n 20 /tmp/backfill.log
pgrep -f "_extract_pdf.py"
```

---

# 附录 A：IMA 收藏 → Obsidian 同步（历史精要，2026-08-13 修正）

> 用户收藏的是「文章」对应 IMA **knowledge-base 模块**（非 notes 模块）。微信文章 `get_media_info` 只给 URL，命令行 WebFetch/curl/真实 Chromium 均拿不到正文（验证墙），故落地为**索引方案**不伪造正文。
> 凭证 `~/.config/ima/client_id`、`~/.config/ima/api_key`；调用 `node .../ima-skills/ima_api.cjs`。skill 版本自检"需更新到 1.1.8"是误报（current 1.1.9），忽略重跑。
> 流程：`_ima_kb_list.py` 拉知识库+条目 → `_gen_ima_index.py` 取 URL 生成 `_IMA收藏索引.md`（按库分组、✅已覆盖/🆕新增）。唯一性检验：标题与现有笔记子串匹配 ≥4 字，绝不重复建笔记。

# 附录 B：抽取质量自检清单（回填后抽查）

- [ ] 抽 1 篇 `◼` 要点型研报：核心观点非空、且未吞入财务表。
- [ ] 抽 1 篇"评级面临的主要风险"标题研报：风险因素正确截断。
- [ ] 风险段尾部无 `投Ta资bl摘e` 类 OCR 碎片。
- [ ] 概念卡 `## 共识综述`：覆盖规模/评级分布/立场/高关注标的/近期脉络齐全。
- [ ] MOC 头部日期 = 当天；Dataview 活清单能列出新增笔记。

---
*SOP 技能包 v2：2026-09-08 由方向 1+3 落地工作沉淀（整合 `_extract_pdf.py`/`_gen_obsidian.py` 已修复项 + 双 vault 拓扑 + 命令速查）。初版 2026-08-13。*
