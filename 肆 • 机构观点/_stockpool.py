#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""近期机构研报股票池：跨全库研报_*.md 按覆盖度排名，生成 Obsidian apex-dashboard 代码块。

排名口径：
  - cover_reports : 该标的被多少篇研报覆盖（同篇多标的计 1 次/标的）
  - cover_orgs    : 覆盖该标的的不同机构数（按 org 去重）
  - top_rating    : 覆盖该标的的评级里，出现次数最多的正向评级（买入/增持/优于大市/推荐/强烈推荐）
输出：
  - 终端打印 Top 40 榜单（调试用）
  - 写出 肆/00-研报股票池.md（含 apex-dashboard 代码块 + Markdown 表格兜底 + Dataview 活清单）
"""
import re
import json
from pathlib import Path
from collections import defaultdict, Counter

REAL = Path("/home/AI/笔记/知识库/肆 • 机构观点")

POSITIVE = ("买入", "增持", "优于大市", "推荐", "强烈推荐", "强推", "买入-A")

def scan():
    rows = []
    for p in REAL.glob("研报_*.md"):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
        if not m:
            continue
        d = {}
        for line in m.group(1).splitlines():
            kv = re.match(r'(\w+):\s*"?([^"\n]*)"?', line)
            if kv:
                d[kv.group(1)] = kv.group(2).strip()
        if "研报" not in d.get("tags", ""):
            continue
        obj = d.get("object", "").strip()
        if not obj:
            continue
        rows.append({
            "object": obj,
            "org": d.get("org", "").strip(),
            "rating": d.get("rating", "").strip(),
            "concept": d.get("concept", "").strip(),
            "date": d.get("declareDate", "").strip(),
        })
    return rows

def main(top=40, out_path=None):
    rows = scan()
    rep_counter = Counter()
    org_counter = defaultdict(set)
    rating_counter = defaultdict(Counter)
    concept_counter = defaultdict(Counter)
    for r in rows:
        rep_counter[r["object"]] += 1
        if r["org"]:
            org_counter[r["object"]].add(r["org"])
        rating_counter[r["object"]][r["rating"]] += 1
        if r["concept"]:
            concept_counter[r["object"]][r["concept"]] += 1

    ranked = []
    for obj, nrep in rep_counter.items():
        norgs = len(org_counter[obj])
        # 主评级：取正向评级里出现最多的；否则取出现最多的评级
        rc = rating_counter[obj]
        pos = {k: v for k, v in rc.items() if any(k.startswith(p) for p in POSITIVE)}
        main_rating = (Counter(pos).most_common(1) or rc.most_common(1) or [("", 0)])[0][0]
        top_concept = concept_counter[obj].most_common(1)[0][0] if concept_counter[obj] else ""
        ranked.append({
            "object": obj,
            "reports": nrep,
            "orgs": norgs,
            "rating": main_rating,
            "concept": top_concept,
        })
    # 排序：覆盖篇数降序，机构数降序
    ranked.sort(key=lambda x: (x["reports"], x["orgs"]), reverse=True)
    ranked = ranked[:top]

    # ---- 终端打印 ----
    print(f"研报总数: {len(rows)}  去重标的: {len(rep_counter)}  Top{top}:")
    for i, x in enumerate(ranked, 1):
        print(f"{i:2d}. {x['object']:<22} 篇数={x['reports']:<3} 机构={x['orgs']:<3} "
              f"主评级={x['rating']:<12} 主概念={x['concept']}")

    # ---- 生成 apex-dashboard 代码块 + 表格 ----
    if out_path:
        dash_lines = [
            "search:",
            "  path: \"肆 • 机构观点\"",
            "  type: task",
            "  sort:",
            "    - cover",
            "  group: false",
            "note:",
            "  title: \"📌 {{value}}\"",
            "  cover: \"{{cover}}\"",
            "  cover-link: \"{{cover-link}}\"",
            "  footer: \"机构覆盖 {{orgs}} 家 · 主评级 {{rating}}\"",
            "card:",
            "  title: true",
            "  content: true",
            "  cover: true",
            "  footer: true",
            "  grid:",
            "    - \"repeat(4, 1fr)\"",
            "    - \"repeat(4, 1fr)\"",
            "    - \"repeat(3, 1fr)\"",
            "  gap: \"1rem\"",
            "  height: 230",
        ]
        table = ["| # | 标的 | 覆盖篇数 | 覆盖机构 | 主评级 | 主概念 |",
                 "|---|------|---------|---------|--------|--------|"]
        for i, x in enumerate(ranked, 1):
            table.append(f"| {i} | {x['object']} | {x['reports']} | {x['orgs']} | "
                         f"{x['rating']} | {x['concept']} |")
        md = [
            "---",
            "tags: [机构观点, 导航, 股票池]",
            "---",
            "",
            "# 近期机构研报股票池",
            "",
            f"> 数据口径：跨「肆 • 机构观点」全部研报笔记（共 {len(rows)} 篇，去重标的 {len(rep_counter)} 只），",
            "按「被覆盖篇数」+「覆盖机构数」排名取 Top。下方 apex-dashboard 为可视化卡片，",
            "下方表格为静态兜底，再下方 Dataview 为活清单（新增研报自动更新）。",
            "",
            "## 🎛️ 机构研报股票池（Apex Dashboard）",
            "",
            "```dashboard",
        ] + dash_lines + [
            "```",
            "",
            "## 静态榜单（Top " + str(top) + "）",
            "",
        ] + table + [
            "",
            "## 活清单（Dataview，新增研报自动聚合）",
            "",
            "```dataview",
            "TABLE org AS 机构, rating AS 评级, concept AS 概念, declareDate AS 日期",
            "FROM \"肆 • 机构观点\"",
            "WHERE contains(tags, \"研报\")",
            "SORT object ASC, declareDate DESC",
            "```",
            "",
        ]
        out_path.write_text("\n".join(md), encoding="utf-8")
        print(f"\n已写出: {out_path}")
    return ranked

if __name__ == "__main__":
    out = REAL / "00-研报股票池.md"
    main(top=40, out_path=out)
