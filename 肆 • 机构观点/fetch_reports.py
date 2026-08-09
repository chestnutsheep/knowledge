#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机构研报采集器 (fetch_reports.py)
================================
定期从「东方财富研报中心(reportapi)」拉取全市场最新券商研报，增量写入 Obsidian
知识库「肆 • 机构观点/」，并刷新 timeline 导航页。

主数据源：东方财富研究报告接口 (reportapi.eastmoney.com/report/list)
  - 支持全市场时间窗拉取 (code=* + beginTime/endTime)
  - 返回字段: title, orgName(机构全称), orgSName(机构短名), stockName/stockCode,
    publishDate, emRatingName(东财评级), researcher(分析师), indvInduName(行业),
    infoCode(用于拼 PDF 链接)
  - PDF 原文: https://pdf.dfcfw.com/pdf/H3_{infoCode}_1.pdf
  - 零 API Key、零依赖，仅需代理 (127.0.0.1:7897) 直连东方财富

补充源（可选）：金融界研报搜索 (JRJ_API_KEY 配置后启用)
  - 字段: title, orgName, declareDate, abstract (无 url)；作为摘要补充/交叉验证

设计要点：
  - 增量更新：已存在的研报笔记按 (orgName, date, title) 跳过。
  - 独立笔记：每篇研报落成「机构观点/机构_日期_标题前18字.md」，含 PDF 链接。
  - timeline 导航页：肆 • 机构观点/00-研报时间线.md，按日期倒序、机构分组。
  - 去重键：笔记文件名 stem（最稳定）。

环境变量：
  JRJ_API_KEY       金融界 API Key (可选，启用补充源)
  VAULT_DIR         Obsidian 库根目录 (默认自动探测)
  DAYS_BACK         回看天数 (默认 7)
  DRY_RUN           置 1 强制样例模式（无需网络/key）
  HTTP_PROXY/HTTPS_PROXY  代理（默认 127.0.0.1:7897，东方财富需代理）

用法：
  python3 fetch_reports.py            # 正常采集（东方财富主源）
  DRY_RUN=1 python3 fetch_reports.py  # 样例模式（无需网络/key）
"""

import os
import sys
import json
import subprocess
import datetime as dt
from pathlib import Path

# ---------- 路径探测 ----------
DEFAULT_VAULT = "/home/AI/scapegoat_data/notebooks/知识库"
VAULT_DIR = Path(os.environ.get("VAULT_DIR", DEFAULT_VAULT))
REAL_DIR = VAULT_DIR / "肆 • 机构观点"

# 代理（东方财富需代理，与项目约定一致：127.0.0.1:7897）
_PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or "http://127.0.0.1:7897"

DRY_RUN = os.environ.get("DRY_RUN", "") == "1"
REPORTS_DIR = REAL_DIR
TIMELINE_FILE = REAL_DIR / "00-研报时间线.md"

DAYS_BACK = int(os.environ.get("DAYS_BACK", "7"))


# ---------- 样例数据（DRY_RUN 时填充，用于验证管线） ----------
SAMPLE_REPORTS = [
    {
        "declareDate": "2026-08-10 09:12:00",
        "orgName": "中信证券",
        "orgSName": "中信证券",
        "title": "A股策略聚焦：轮动减速，坚守核心资产",
        "abstract": "我们认为市场短期进入轮动减速期，建议从中报兑现度出发坚守AI算力、半导体设备与高股息核心资产，规避纯主题炒作。",
        "stockName": "", "stockCode": "", "rating": "推荐",
        "researcher": "裘翔", "industry": "策略", "pdfUrl": "",
    },
    {
        "declareDate": "2026-08-10 08:40:00",
        "orgName": "华泰证券",
        "orgSName": "华泰证券",
        "title": "中期策略：全球流动性拐点下的资产配置",
        "abstract": "美联储降息预期修正，全球流动性边际收紧；维持对有色、原油等全球定价品的低配，增配对宏观脱敏的红利与公用事业。",
        "stockName": "", "stockCode": "", "rating": "中性",
        "researcher": "张继强", "industry": "策略", "pdfUrl": "",
    },
    {
        "declareDate": "2026-08-09 21:05:00",
        "orgName": "中金公司",
        "orgSName": "中金公司",
        "title": "新质生产力系列：商业航天产业链全景",
        "abstract": "商业航天进入密集发射期，卫星制造、星载设备、地面终端三环节依次受益，关注具备批产能力的配套企业。",
        "stockName": "", "stockCode": "", "rating": "推荐",
        "researcher": "陈显顺", "industry": "航天", "pdfUrl": "",
    },
    {
        "declareDate": "2026-08-09 17:30:00",
        "orgName": "国泰海通",
        "orgSName": "国泰海通",
        "title": "食品饮料下半年策略：确定性优先",
        "abstract": "需求弱复苏背景下，白酒聚焦头部集中度提升，大众品优选成本下行+份额扩张双逻辑标的。",
        "stockName": "", "stockCode": "", "rating": "增持",
        "researcher": "訾猛", "industry": "食品饮料", "pdfUrl": "",
    },
    {
        "declareDate": "2026-08-08 15:50:00",
        "orgName": "广发证券",
        "orgSName": "广发证券",
        "title": "储能出海深度：欧美大储放量拐点",
        "abstract": "欧美大储并网加速，系统级集成与PCS具备全球竞争力，看好出海订单兑现度高的头部厂商。",
        "stockName": "", "stockCode": "", "rating": "买入",
        "researcher": "陈子坤", "industry": "储能", "pdfUrl": "",
    },
]


def safe_name(s: str, limit: int = 18) -> str:
    """生成安全的文件名片段（去非法字符、截断）。"""
    bad = '/\\:*?"<>|'
    for c in bad:
        s = s.replace(c, "")
    s = s.strip()
    return s[:limit]


def _norm_date(s: str) -> str:
    """把东方财富 publishDate(含毫秒) 归一为 YYYY-MM-DD HH:MM:SS。"""
    if not s:
        return ""
    s = s.replace("T", " ").replace(".000", "")
    # 取到秒
    if len(s) >= 19:
        return s[:19]
    if len(s) >= 10:
        return s[:10] + " 00:00:00"
    return s


def fetch_via_eastmoney(days_back: int) -> list:
    """调用东方财富研报中心接口，拉取全市场近 days_back 天研报。

    接口: https://reportapi.eastmoney.com/report/list
    参数: code=* (全市场), beginTime/endTime 时间窗, pageSize 分页
    返回统一结构 list[dict]，字段含 pdfUrl。
    """
    try:
        import requests
    except Exception as e:
        print(f"[ERROR] requests 不可用: {e}", file=sys.stderr)
        return []

    end = dt.datetime.now()
    start = end - dt.timedelta(days=days_back)
    begin = start.strftime("%Y-%m-%d")
    end_s = end.strftime("%Y-%m-%d")
    url = "https://reportapi.eastmoney.com/report/list"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://data.eastmoney.com/report/stock.jshtml",
        "Accept": "*/*",
    }
    proxies = {"http": _PROXY, "https": _PROXY} if _PROXY else None

    out = []
    page = 1
    page_size = 100
    try:
        while True:
            params = {
                "industryCode": "*", "pageSize": str(page_size),
                "industry": "*", "rating": "*", "ratingChange": "*",
                "beginTime": begin, "endTime": end_s,
                "pageNo": str(page), "fields": "", "qType": "0",
                "orgCode": "", "code": "*", "rcode": "",
                "p": str(page), "pageNum": str(page), "pageNumber": str(page),
                "_": str(int(dt.datetime.now().timestamp() * 1000)),
            }
            r = requests.get(url, params=params, headers=headers,
                             proxies=proxies, timeout=30)
            data = r.json()
            rows = data.get("data") or []
            total_page = data.get("TotalPage", 1)
            for it in rows:
                info_code = it.get("infoCode", "")
                pdf = f"https://pdf.dfcfw.com/pdf/H3_{info_code}_1.pdf" if info_code else ""
                org = it.get("orgSName") or it.get("orgName") or "未知机构"
                out.append({
                    "declareDate": _norm_date(it.get("publishDate", "")),
                    "orgName": org,
                    "orgFullName": it.get("orgName", ""),
                    "title": it.get("title", ""),
                    "abstract": "",  # 东方财富列表无摘要，置空（笔记以 PDF 原文为准）
                    "stockName": it.get("stockName", ""),
                    "stockCode": it.get("stockCode", ""),
                    "rating": it.get("emRatingName") or it.get("sRatingName") or "",
                    "researcher": it.get("researcher", ""),
                    "industry": it.get("indvInduName", ""),
                    "pdfUrl": pdf,
                    "source": "东方财富研报中心",
                })
            if page >= total_page or not rows:
                break
            page += 1
            if page > 20:  # 安全上限
                break
    except Exception as e:
        print(f"[ERROR] 东方财富接口异常: {e}", file=sys.stderr)
        return out
    return out


def fetch_via_jrj(days_back: int) -> list:
    """可选补充源：金融界研报摘要。需 JRJ_API_KEY。返回统一结构。"""
    if not os.environ.get("JRJ_API_KEY"):
        return []
    skill_dir = Path(os.environ.get("JRJ_SKILL_DIR",
                      "/home/scapegoat/.codebuddy/skills/jrj-fin-search-skill"))
    end = dt.datetime.now()
    start = end - dt.timedelta(days=days_back)
    start_s = start.strftime("%Y-%m-%d 00:00:00")
    cmd = ["node", str(skill_dir / "scripts" / "news.js"), "reports",
           "--keywords", "策略 行业 公司 深度 宏观 专题",
           "--start", start_s, "--limit", "200", "--format", "json"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except Exception as e:
        print(f"[ERROR] 金融界调用失败: {e}", file=sys.stderr)
        return []
    if out.returncode != 0:
        print(f"[WARN] 金融界未返回(可能 key 失效): {out.stderr[:200]}", file=sys.stderr)
        return []
    try:
        data = json.loads(out.stdout)
        items = data.get("data", {}).get("items", [])
    except Exception:
        return []
    res = []
    for it in items:
        res.append({
            "declareDate": it.get("declareDate", ""),
            "orgName": it.get("orgName", "未知机构"),
            "orgFullName": it.get("orgName", ""),
            "title": it.get("title", ""),
            "abstract": it.get("abstract", ""),
            "stockName": "", "stockCode": "", "rating": "",
            "researcher": "", "industry": "", "pdfUrl": "",
            "source": "金融界研报摘要",
        })
    return res


def write_report_note(r: dict) -> str:
    """为单篇研报写独立笔记；已存在则跳过。返回笔记相对路径或 None。"""
    org = r.get("orgName", "未知机构")
    date = (r.get("declareDate") or "")[:10]
    title = r.get("title", "未命名研报")
    abstract = r.get("abstract", "")
    pdf = r.get("pdfUrl", "")
    rating = r.get("rating", "")
    stock = r.get("stockName", "")
    stock_code = r.get("stockCode", "")
    researcher = r.get("researcher", "")
    industry = r.get("industry", "")
    src = r.get("source", "东方财富研报中心")

    fname = f"{org}_{date}_{safe_name(title)}.md"
    fpath = REPORTS_DIR / fname
    if fpath.exists():
        return None  # 增量跳过

    stock_line = f"｜ 标的：{stock}({stock_code})" if stock else ""
    rating_line = f"｜ 评级：{rating}" if rating else ""
    indu_line = f"｜ 行业：{industry}" if industry else ""
    research_line = f"｜ 分析师：{researcher}" if researcher else ""
    pdf_line = f"\n> 原文 PDF：{pdf}" if pdf else "\n> 原文：详见东方财富研报中心（列表无直链）"

    content = f"""---
tags:
  - 机构观点
  - 研报
org: "{org}"
declareDate: "{date}"
source: "{src}"
---
# {title}（{org} {date}）

> [!note] 来源
> {org}《{title}》
> 发布日期：{date} ｜ 数据来源：{src}{stock_line}{rating_line}{indu_line}{research_line}{pdf_line}

## 核心观点

{abstract if abstract else "（东方财富列表接口未提供摘要，请点击上方原文 PDF 阅读完整观点）"}

## 知识库交叉引用

- 待关联：在相关产业链/概念笔记中通过 [[{org}_{date}_{safe_name(title)}]] 引用

## 风险因素

- 详见原研报正文

---
*本文档由机构研报采集器自动生成（{dt.datetime.now().strftime('%Y-%m-%d %H:%M')}）｜源：{src}*
"""
    fpath.write_text(content, encoding="utf-8")
    return f"肆 • 机构观点/{fname}"


def build_timeline(records: list):
    """根据全部研报记录（含历史文件扫描）重建 timeline 导航页。"""
    def sort_key(x):
        return x.get("declareDate") or "0000"
    records.sort(key=sort_key, reverse=True)

    by_date = {}
    for rec in records:
        d = (rec.get("declareDate") or "未知日期")[:10]
        by_date.setdefault(d, []).append(rec)

    lines = []
    lines.append("---")
    lines.append("tags:")
    lines.append("  - 机构观点")
    lines.append("  - timeline")
    lines.append("---")
    lines.append("")
    lines.append("# 机构研报时间线（自动更新）")
    lines.append("")
    lines.append("> 本页由「机构研报采集器」每个交易日 16:30 自动刷新。")
    lines.append("> 展示**哪家机构 / 哪天 / 更新了什么观点**的研报。主数据源：东方财富研报中心（含原文 PDF）。")
    lines.append("> 点击条目跳转对应研报笔记（独立成篇，含原文链接）。")
    lines.append("")
    lines.append(f"> 最近更新：{dt.datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ 共收录 {len(records)} 篇")
    lines.append("")
    for d in sorted(by_date.keys(), reverse=True):
        lines.append(f"## {d}")
        lines.append("")
        for rec in sorted(by_date[d], key=lambda x: x.get("orgName", "")):
            org = rec.get("orgName", "未知机构")
            title = rec.get("title", "")
            note = rec.get("note_rel", "")
            # 一句话/标签：评级+行业+标的
            tags = []
            if rec.get("rating"):
                tags.append(rec["rating"])
            if rec.get("industry"):
                tags.append(rec["industry"])
            if rec.get("stockName"):
                tags.append(rec["stockName"])
            tag_str = "【" + "/".join(tags) + "】" if tags else ""
            if note:
                note_name = Path(note).stem
                lines.append(f"- **{org}** ｜ [[{note_name}]] {tag_str}{title}")
            else:
                lines.append(f"- **{org}** ｜ {title} {tag_str}")
        lines.append("")

    TIMELINE_FILE.write_text("\n".join(lines), encoding="utf-8")


def scan_existing_notes() -> list:
    """扫描目录下已有研报笔记，提取 timeline 记录（兼容新旧两种格式）。"""
    import re
    recs = []
    if not REPORTS_DIR.exists():
        return recs
    for f in REPORTS_DIR.glob("*.md"):
        if f.name.startswith("00-"):
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        org_m = re.search(r'org:\s*"([^"]+)"', text)
        date_m = re.search(r'declareDate:\s*"([^"]+)"', text)
        title_m = re.search(r'^#\s+(.+)$', text, re.M)
        org = org_m.group(1) if org_m else None
        date = date_m.group(1) if date_m else None
        fn_m = re.search(r'（(.+?)(\d{4}-\d{2}-\d{2})）', f.stem)
        if not org and fn_m:
            org = fn_m.group(1)
        if not date and fn_m:
            date = fn_m.group(2)
        title = title_m.group(1) if title_m else f.stem
        if org and date and title.endswith(f"（{org} {date}）"):
            title = title[: -(len(org) + len(date) + 4)]
        recs.append({
            "declareDate": (date + " 00:00:00") if date else "0000",
            "orgName": org or "未知机构",
            "title": title,
            "abstract": "",
            "stem": f.stem,
            "note_rel": f"肆 • 机构观点/{f.name}",
        })
    return recs


def main():
    print(f"[INFO] 模式: {'DRY_RUN(样例)' if DRY_RUN else '真实拉取(东方财富主源)'} | 回看 {DAYS_BACK} 天")

    if DRY_RUN:
        items = SAMPLE_REPORTS
        print(f"[INFO] 样例研报 {len(items)} 篇")
    else:
        items = fetch_via_eastmoney(DAYS_BACK)
        print(f"[INFO] 东方财富返回研报 {len(items)} 篇")
        # 可选补充：金融界摘要（若配 key）
        if os.environ.get("JRJ_API_KEY"):
            jrj = fetch_via_jrj(DAYS_BACK)
            print(f"[INFO] 金融界补充 {len(jrj)} 篇")
            items = items + jrj

    # 写独立笔记（增量）
    new_count = 0
    for r in items:
        rel = write_report_note(r)
        if rel:
            new_count += 1
            print(f"[NEW] {rel}")
        else:
            print(f"[SKIP] 已存在: {r.get('orgName')} {r.get('title')}")

    # 合并历史记录 + 新写入记录，重建 timeline
    existing = scan_existing_notes()
    seen = set()
    merged = []
    for rec in existing:
        key = rec.get("stem")
        if key in seen:
            continue
        seen.add(key)
        merged.append(rec)
    for r in items:
        org = r.get("orgName", "未知机构")
        date = (r.get("declareDate") or "")[:10]
        stem = f"{org}_{date}_{safe_name(r.get('title', ''))}"
        if stem in seen:
            continue
        seen.add(stem)
        fname = stem + ".md"
        note_rel = f"肆 • 机构观点/{fname}" if (REPORTS_DIR / fname).exists() else ""
        merged.append({
            "declareDate": r.get("declareDate", ""),
            "orgName": org,
            "title": r.get("title", ""),
            "abstract": r.get("abstract", ""),
            "rating": r.get("rating", ""),
            "industry": r.get("industry", ""),
            "stockName": r.get("stockName", ""),
            "stem": stem,
            "note_rel": note_rel,
        })

    build_timeline(merged)
    print(f"[DONE] timeline 已更新: {TIMELINE_FILE} | 总收录 {len(merged)} 篇（本次新增 {new_count}）")


if __name__ == "__main__":
    main()
