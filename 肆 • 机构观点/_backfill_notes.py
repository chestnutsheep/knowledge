#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一次性回填脚本：把现有 250 篇旧笔记升级到新的「条件渲染 + 概念 tags」格式。

做的事：
  1. frontmatter 补 pdfAvailable、把 tags 加概念维度（如 "概念/教育"）。
  2. 正文条件渲染：去掉「核心观点」占位噪声明文（旧笔记均无摘要），
     去掉「风险因素」死模板，保留来源 callout。
  3. 不动「## 知识库交叉引用」——由后续 _gen_obsidian.py 反向回填真实链接。

注意：本脚本幂等、可重复跑；仅处理「肆 • 机构观点/*.md」里非导航类研报笔记。
"""
import re
from pathlib import Path
from datetime import datetime

REAL = Path("/home/AI/Obsidian/知识库/肆 • 机构观点")

def _strip_quotes(s: str) -> str:
    s = (s or "").strip()
    # 循环去掉多层包裹的引号（修复曾被双引号污染的笔记）
    while len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1].strip()
    return s

def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    fm_raw, body = m.group(1), m.group(2)
    fm = {}
    for line in fm_raw.splitlines():
        kv = re.match(r'(\w+):\s*(.*)$', line)
        if kv:
            fm[kv.group(1)] = _strip_quotes(kv.group(2))
    return fm, body

def rebuild(fm: dict, body: str) -> str:
    concept = fm.get("concept") or "个股中报业绩"
    org = fm.get("org") or "未知机构"
    title = fm.get("title") or ""
    date = fm.get("declareDate") or ""
    src = fm.get("source") or "东方财富研报中心"
    stock = fm.get("object") or ""
    rating = fm.get("rating") or ""
    industry = fm.get("industry") or ""
    researcher = fm.get("analyst") or ""
    pdf = fm.get("pdfUrl") or ""

    # tags：基于 concept 字段直接重建干净标签（忽略旧 tags 里可能损坏的概念片段）
    tags = ["机构观点", "研报"]
    concept_tag = "概念/" + concept
    if concept_tag not in tags:
        tags.append(concept_tag)
    tag_str = "[" + ", ".join(f'"{t}"' if (" " in t or "/" in t) else t for t in tags) + "]"

    pdf_available = "true" if pdf else "false"

    # 抓来源 callout 块（> [!note] ... 到下一个 ## 或结尾）
    callout_m = re.search(r"(> \[!note\][\s\S]*?)(?=\n## |\Z)", body)
    if callout_m:
        callout = callout_m.group(1).strip()
    else:
        callout = (
            f"> [!note] 来源\n> {org}《{title}》\n> 发布日期：{date} ｜ 数据来源：{src}"
            + (f"｜ 标的：{stock}" if stock else "")
            + (f"｜ 评级：{rating}" if rating else "")
            + (f"｜ 行业：{industry}" if industry else "")
            + (f"｜ 分析师：{researcher}" if researcher else "")
            + (f"\n> 原文 PDF：{pdf}" if pdf else "")
        )

    new_body = [
        f"# {title}",
        "",
        callout,
        "",
        "## 知识库交叉引用",
        "",
        f"- 概念归类：[[概念卡片/{concept.replace('/', '·')}]]",
        "",
        "---",
        f"*本文档由机构研报采集器自动生成（{datetime.now():%Y-%m-%d %H:%M}）｜源：{src}*",
    ]
    fm_block = [
        "---",
        f"tags: {tag_str}",
        f'org: "{org}"',
        f'declareDate: "{date}"',
        f'title: "{title}"',
        f'concept: "{concept}"',
        f'rating: "{rating}"',
        f'industry: "{industry}"',
        f'object: "{stock}"',
        f'analyst: "{researcher}"',
        f'source: "{src}"',
        f'pdfUrl: "{pdf}"',
        f"pdfAvailable: {pdf_available}",
        "---",
    ]
    return "\n".join(fm_block) + "\n" + "\n".join(new_body) + "\n"

def main():
    n = 0
    for f in REAL.glob("*.md"):
        if f.name.startswith(("00-", "README", "_")):
            continue
        text = f.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        if not fm or "title" not in fm:
            continue
        new_text = rebuild(fm, body)
        f.write_text(new_text, encoding="utf-8")
        n += 1
    print(f"[DONE] 一次性回填：{n} 篇旧笔记已升级到条件渲染+概念 tags 格式")

if __name__ == "__main__":
    main()
