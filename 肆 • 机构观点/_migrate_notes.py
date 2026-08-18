#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性迁移：把旧格式研报笔记（机构_日期_长标题.md）重写为新格式。

新格式：
  - 文件名：研报_YYYYMMDD_NNN.md（短 ID，不塞标题）
  - frontmatter 补全：title / concept / rating / industry / object / analyst / pdfUrl / source
  - 正文 H1 用 title；交叉引用 [[旧stem]] -> [[新ID]

迁移后，全 vault 范围内所有对旧 stem 的 [[wikilink]] 也会被替换为新 ID。
概念归类复用 fetch_reports.classify（单一真相）。
"""
import re, json
from pathlib import Path
from datetime import datetime

REAL = Path("/home/AI/Obsidian/知识库/肆 • 机构观点")
VAULT = Path("/home/AI/Obsidian/知识库")

# 复用统一概念归类
import importlib.util
spec = importlib.util.spec_from_file_location("fr", REAL / "fetch_reports.py")
fr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fr)
classify = fr.classify

OLD_BAD = '/\\:*?"<>|'

def old_stem_to_fields(p):
    """从旧笔记解析结构化字段。返回 (org, date, title, pdf, rating, industry, object, analyst)。"""
    txt = p.read_text(encoding="utf-8", errors="ignore")
    fm = {}
    m = re.match(r"^---\n(.*?)\n---", txt, re.S)
    if m:
        for line in m.group(1).splitlines():
            kv = re.match(r'(\w+):\s*"?([^"\n]*)"?', line)
            if kv:
                fm[kv.group(1)] = kv.group(2).strip()
    org = fm.get("org", "")
    date = (fm.get("declareDate") or "")[:10]
    # title：优先 frontmatter（新版可能已有），否则从 H1 去后缀
    title = fm.get("title", "")
    if not title:
        h = re.search(r'^#\s+(.+)$', txt, re.M)
        title = h.group(1) if h else p.stem
        if org and date and title.endswith(f"（{org} {date}）"):
            title = title[: -(len(org) + len(date) + 4)]
    # pdf / 其他从 callout 正文抓
    pdf = ""
    pm = re.search(r'原文 PDF：(https?://\S+)', txt)
    if pm:
        pdf = pm.group(1)
    rating = fm.get("rating", "")
    industry = fm.get("industry", "")
    object_ = fm.get("object", "")
    analyst = fm.get("analyst", "")
    if not object_:
        om = re.search(r'标的[：:]\s*([^\｜|\n]+)', txt)
        if om:
            object_ = om.group(1).strip()
    if not rating:
        rm = re.search(r'评级[：:]\s*([^\｜|\n]+)', txt)
        if rm:
            rating = rm.group(1).strip()
    if not industry:
        im = re.search(r'行业[：:]\s*([^\｜|\n]+)', txt)
        if im:
            industry = im.group(1).strip()
    if not analyst:
        am = re.search(r'分析师[：:]\s*([^\｜|\n]+)', txt)
        if am:
            analyst = am.group(1).strip()
    return org, date, title, pdf, rating, industry, object_, analyst

def main():
    # 1) 找出旧格式研报笔记（文件名含 _日期_ 且非新 ID 开头）
    old_notes = []
    for f in REAL.glob("*.md"):
        if f.name.startswith(("00-", "README", "_")):
            continue
        if f.name.startswith("研报_"):
            continue  # 已是新格式
        old_notes.append(f)
    print(f"[INFO] 待迁移旧笔记: {len(old_notes)} 篇")

    # 2) 解析字段 + 按日期分组分配新 ID
    mapping = {}        # 旧 stem -> 新 ID
    new_records = {}    # 新 ID -> 字段
    by_date = {}
    for f in old_notes:
        org, date, title, pdf, rating, industry, object_, analyst = old_stem_to_fields(f)
        by_date.setdefault(date, []).append((f, org, title, pdf, rating, industry, object_, analyst))

    for date, items in by_date.items():
        # 同日按原标题排序，保证 ID 稳定
        items.sort(key=lambda x: x[2])
        for seq, (f, org, title, pdf, rating, industry, object_, analyst) in enumerate(items, 1):
            d = date.replace("-", "")
            nid = f"研报_{d}_{seq:03d}"
            # 防碰撞
            while (REAL / f"{nid}.md").exists():
                seq += 1
                nid = f"研报_{d}_{seq:03d}"
            concept = classify(industry, title)
            mapping[f.stem] = nid
            new_records[nid] = dict(org=org, date=date, title=title, pdf=pdf,
                                    rating=rating, industry=industry, object=object_,
                                    analyst=analyst, concept=concept, old_stem=f.stem)

    # 3) 重写旧笔记为新格式文件，并删除旧文件
    for nid, rec in new_records.items():
        org = rec["org"] or "未知机构"
        date = rec["date"]
        title = rec["title"]
        pdf = rec["pdf"]
        rating = rec["rating"]
        industry = rec["industry"]
        object_ = rec["object"]
        analyst = rec["analyst"]
        concept = rec["concept"]
        src = "东方财富研报中心"
        stock_line = f"｜ 标的：{object_}" if object_ else ""
        rating_line = f"｜ 评级：{rating}" if rating else ""
        indu_line = f"｜ 行业：{industry}" if industry else ""
        research_line = f"｜ 分析师：{analyst}" if analyst else ""
        pdf_line = f"\n> 原文 PDF：{pdf}" if pdf else "\n> 原文：详见东方财富研报中心（列表无直链）"
        content = f"""---
tags: [机构观点, 研报]
org: "{org}"
declareDate: "{date}"
title: "{title}"
concept: "{concept}"
rating: "{rating}"
industry: "{industry}"
object: "{object_}"
analyst: "{analyst}"
source: "{src}"
pdfUrl: "{pdf}"
---
# {title}

> [!note] 来源
> {org}《{title}》
> 发布日期：{date} ｜ 数据来源：{src}{stock_line}{rating_line}{indu_line}{research_line}{pdf_line}

## 核心观点

（东方财富列表接口未提供摘要，请点击上方原文 PDF 阅读完整观点）

## 知识库交叉引用

- 待关联：在相关产业链/概念笔记中通过 [[{nid}]] 引用

## 风险因素

- 详见原研报正文

---
*本文档由机构研报采集器自动生成（{datetime.now():%Y-%m-%d %H:%M}）｜源：{src}*
"""
        (REAL / f"{nid}.md").write_text(content, encoding="utf-8")
        # 删旧文件
        old_path = REAL / f"{rec['old_stem']}.md"
        if old_path.exists():
            old_path.unlink()
    print(f"[INFO] 已重写 {len(new_records)} 篇为新格式（旧文件已删除）")

    # 4) 全 vault 替换 [[旧stem]] -> [[新ID]]
    #    注意旧 stem 可能出现在 wikilink（[[...]]）、概念卡片表格链接、canvas 等
    count_replaced = 0
    file_count = 0
    for md in VAULT.rglob("*.md"):
        if md.name.startswith("_"):
            continue
        txt = md.read_text(encoding="utf-8", errors="ignore")
        new_txt = txt
        for old_stem, nid in mapping.items():
            # 替换 wikilink 中的旧 stem（[[old_stem]] 或 [[old_stem|别名]]）
            new_txt = re.sub(r'\[\[(?:\s*)' + re.escape(old_stem) + r'(?:\s*\|[^\]]*)?\]\]',
                             f'[[{nid}]]', new_txt)
            # 也替换裸文本引用（如 timeline 里的 [[old stem]] 已覆盖；额外兜底出现在表格但无括号的极少见）
        if new_txt != txt:
            md.write_text(new_txt, encoding="utf-8")
            file_count += 1
            count_replaced += sum(1 for _ in re.finditer(r'\[\[' + re.escape(nid) + r'\]\]', new_txt))
    print(f"[INFO] 全 vault 引用替换：涉及 {file_count} 个文件；新 ID 被引用处约 {count_replaced}")

    # 5) 写出映射表（备查/回滚）
    (REAL / "_migrate_map.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[DONE] 迁移完成，映射表已存 _migrate_map.json")

if __name__ == "__main__":
    main()
