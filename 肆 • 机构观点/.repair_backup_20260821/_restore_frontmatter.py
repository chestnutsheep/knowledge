#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
紧急恢复脚本：从 _meta.json 恢复被 _extract_pdf.backfill_note 误清空的前端字段
（org/title/declareDate/concept/object/industry/rating/tags）。
同时尽量保留已抽取的正文章节（核心观点/盈利预测/投资建议/风险因素/知识库交叉引用）。
pdfUrl：若 _pdf_cache 存在同名 pdf 则标记为可得，真实 URL 由后续 _refetch_pdfurl.py 补充；
        否则置空 pdfAvailable=false。

幂等可重跑。不破坏已抽取内容。
"""
import re
import json
from pathlib import Path

REAL = Path("/home/AI/Obsidian/知识库/肆 • 机构观点")
CACHE = REAL / "_pdf_cache"
meta = json.load(open(REAL / "_meta.json", encoding="utf-8"))

# 正文章节名（需保留，不被 frontmatter 恢复破坏）
KEEP_SECTIONS = ["核心观点", "盈利预测", "投资建议", "风险因素", "知识库交叉引用"]

def split_body(body: str):
    """把正文拆成：callout、各章节(dict)、footer。"""
    callout_m = re.search(r"(> \[!note\][\s\S]*?)(?=\n# |\Z)", body)
    callout = callout_m.group(1).strip() if callout_m else ""
    # 若没有标准 callout，尝试抓第一行标题后到第一个 ## 的内容
    if not callout:
        m = re.search(r"# .*?\n(.*?)(?=\n## )", body, re.S)
        callout = m.group(1).strip() if m else ""
    sections = {}
    # 按 ## 章节切
    parts = re.split(r"\n## (.+?)\n", body)
    # parts[0] 是标题+callout 之前，parts[1:] 是 (章节名, 内容) 交替
    for i in range(1, len(parts), 2):
        name = parts[i].strip()
        content = parts[i+1].strip() if i+1 < len(parts) else ""
        sections[name] = content
    footer_m = re.search(r"(\n---[\s\S]*)$", body)
    footer = footer_m.group(1).strip() if footer_m else ""
    return callout, sections, footer

def parse_frontmatter(t):
    """健壮解析：以开头 --- 起，结尾 --- 或首个 # 标题前为 frontmatter。
    兼容「缺结尾 ---」的损坏笔记。返回 (fm_raw, body) 或 None。"""
    if not t.startswith("---"):
        return None
    # 去掉开头 --- 及紧随的空行
    rest = t[3:]
    rest = rest.lstrip("\n")
    # 找结尾 --- ：单独成行的 ---（前后可空行），或第一个出现的 # 标题
    # 优先：第一个独立 --- 行
    m = re.search(r"\n[ \t]*---\n", "\n" + rest)
    if m:
        fm_raw = rest[:m.start()]
        body = rest[m.end()-1:]  # 吃掉结尾 --- 后的换行
        return fm_raw, body.lstrip("\n")
    # 无结尾 --- ：取第一个 # 标题之前为 frontmatter
    m2 = re.search(r"\n#\s", "\n" + rest)
    if m2:
        fm_raw = rest[:m2.start()]
        body = rest[m2.start():]
        return fm_raw, body.lstrip("\n")
    return None

def main():
    import sys
    DRY = "--dry" in sys.argv
    n_fixed = 0
    n_parsed = 0
    for f in sorted(REAL.glob("研报_*.md")):
        stem = f.stem
        if stem not in meta:
            continue
        md = meta[stem]
        t = f.read_text(encoding="utf-8", errors="ignore")
        parsed = parse_frontmatter(t)
        if not parsed:
            continue
        n_parsed += 1
        fm_raw, body = parsed
        # 当前 frontmatter（可能残缺）
        cur = {}
        for ln in fm_raw.splitlines():
            kv = re.match(r'(\w+):\s*(.*)$', ln)
            if kv:
                cur[kv.group(1)] = kv.group(2).strip().strip('"')

        # 是否真的残缺（缺关键字段）
        need = ["org", "title", "declareDate", "concept"]
        if all(cur.get(k) for k in need):
            continue  # 已完整，跳过

        # 从 meta 恢复
        concept = md.get("concept", "个股中报业绩")
        org = md.get("org", "")
        title = md.get("title", "") or f.name
        date = md.get("date", "")
        obj = md.get("object", "")
        industry = md.get("industry", "")
        rating = md.get("rating", "")
        # 保留已抽的更精确 rating/forecast（若 cur 有且非空）
        if cur.get("rating"):
            rating = cur["rating"]
        forecast = cur.get("forecast", "")
        # tags
        tags = ["机构观点", "研报", f"概念/{concept}"]

        callout, sections, footer = split_body(body)
        # 重建 callout（若原 callout 缺失，生成标准来源 callout）
        if not callout:
            callout = (
                f"> [!note] 来源\n> {org}《{title}》\n> 发布日期：{date} ｜ 数据来源：东方财富研报中心"
                + (f"｜ 标的：{obj}" if obj else "")
                + (f"｜ 评级：{rating}" if rating else "")
                + (f"｜ 行业：{industry}" if industry else "")
            )

        # pdfUrl：若缓存有则标记可得（URL 后续补），否则空
        has_cache = (CACHE / f"{stem}.pdf").exists()
        pdf_url = cur.get("pdfUrl", "") if cur.get("pdfUrl") else ""
        if has_cache and not pdf_url:
            pdf_url = ""  # 链接待 _refetch_pdfurl 补
        pdf_avail = "true" if (pdf_url or has_cache) else "false"

        # 重建 frontmatter
        fm_lines = ["---"]
        fm_lines.append(f'tags: [{", ".join(chr(34)+x+chr(34) if (" " in x or "/" in x) else x for x in tags)}]')
        fm_lines.append(f'org: "{org}"')
        fm_lines.append(f'declareDate: "{date}"')
        fm_lines.append(f'title: "{title}"')
        fm_lines.append(f'concept: "{concept}"')
        if rating:
            fm_lines.append(f'rating: "{rating}"')
        if industry:
            fm_lines.append(f'industry: "{industry}"')
        if obj:
            fm_lines.append(f'object: "{obj}"')
        fm_lines.append(f'source: "东方财富研报中心"')
        fm_lines.append(f'pdfUrl: "{pdf_url}"')
        fm_lines.append(f"pdfAvailable: {pdf_avail}")
        if forecast:
            fm_lines.append(f'forecast: "{forecast}"')
        fm_block = "\n".join(fm_lines) + "\n"

        # 重组正文：标题 + callout + 保留章节（按固定顺序）
        new_body = [f"# {title}", "", callout, ""]
        for sec in KEEP_SECTIONS:
            if sec in sections and sections[sec].strip():
                new_body += [f"## {sec}", "", sections[sec].strip(), ""]
        # footer
        if footer:
            new_body.append(footer)
        else:
            new_body.append("---")
            new_body.append(f"*本文档由机构研报采集器自动生成｜源：东方财富研报中心*")

        if DRY:
            if n_fixed < 3:
                print(f"--- [{f.name}] 重建预览 ---")
                print(fm_block.rstrip())
                print("  # callout 首行:", (callout.splitlines()[0] if callout else "<空>"))
                print("  保留章节:", [s for s in KEEP_SECTIONS if s in sections and sections[s].strip()])
            n_fixed += 1
            continue
        f.write_text(fm_block + "\n" + "\n".join(new_body).rstrip() + "\n", encoding="utf-8")
        n_fixed += 1
    print(f"[RESTORE] 可解析={n_parsed} 将恢复={n_fixed} 篇")

if __name__ == "__main__":
    main()
