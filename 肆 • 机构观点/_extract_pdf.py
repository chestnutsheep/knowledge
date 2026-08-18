#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
研报 PDF 内容抽取器：把东方财富研报 PDF 的「核心内容」抽成结构化文本，
回填到对应研报笔记，让知识库从「只有链接」升级为「可读内容」。

抽取策略（稳健、可降级，绝不编造）：
  - 用 pdfplumber 提取全部页文本
  - 核心观点：截取正文第一段业绩概述（去广告/免责声明/页眉页脚噪声）
  - 盈利预测：正则抓 "归母净利润至 X/Y/Z 亿元，对应 PE 为 A/B/C 倍"
  - 投资评级：首页 "优于大市(维持)" / 正文 "维持"xxx"评级"
  - 风险因素：抓 "风险提示：...（到投资建议或段落尾）"
  - 投资建议：抓 "投资建议：..."
  - 若某段抽不到 → 留空，笔记里该章节不生成（条件渲染）

依赖：pdfplumber（已装）、代理在线（pdf.dfcfw.com 走直连，但稳妥起见仍用系统网络）
"""
import re
import ssl
import json
import urllib.request
from pathlib import Path
from datetime import datetime

import pdfplumber

REAL = Path("/home/AI/Obsidian/知识库/肆 • 机构观点")
CACHE = REAL / "_pdf_cache"
CACHE.mkdir(exist_ok=True)

# ---------- 噪声清洗 ----------
NOISE_PATTERNS = [
    r"请务必阅读正文之后的免责声明及其项下所有内容.*",
    r"证券研究报告[|\s]*\d{4}年\d{1,2}月\d{1,2}日",
    r"资料来源[:：].*",
    r"相关研究报告",
    r"市场走势",
    r"基础数据",
    r"投资评级.*",
    r"合理估值.*",
    r"收盘价.*",
    r"总市值.*",
    r"52周.*",
    r"近3个月.*",
    r"证券分析师[:：].*",
    r"^\s*[\d\-]+\s*$",
    r"公司研究[·•].*",
    r"社会服务[·•].*",
]

def clean_line(line: str) -> str:
    s = line.strip()
    if not s:
        return ""
    for p in NOISE_PATTERNS:
        if re.search(p, s):
            return ""
    # 去掉页眉孤字（如 "证券研究报告" 行）
    if s in ("证券研究报告", "核心观点", "丽江股份（002033.SZ）"):
        return ""
    return s

def download_pdf(url: str) -> bytes | None:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        return urllib.request.urlopen(req, timeout=40, context=ctx).read()
    except Exception as e:
        print(f"  [DL ERR] {url} -> {e}")
        return None

def pdf_to_text(pdf_bytes: bytes) -> str:
    import io
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        pages = [pg.extract_text() or "" for pg in pdf.pages]
    return "\n".join(pages)

# ---------- 结构化抽取 ----------
# 首页页眉/侧栏噪声词（双栏排版会混入正文流）
HEADER_NOISE = [
    "公司研究", "财报点评", "社会服务", "旅游及景区", "证券分析师", "投资评级",
    "基础数据", "合理估值", "收盘价", "总市值", "流通市值", "52周", "近3个月",
    "市场走势", "相关研究报告", "资料来源", "请务必阅读", "研究·", "·财报",
    "盈利预测和财务指标", "财务预测与估值", "资产负债表", "利润表", "现金流量表",
    "关键财务", "沪深市场", "联系方式", "分析师承诺", "国信证券经济研究所",
]

def strip_noise(s: str) -> str:
    for w in HEADER_NOISE:
        s = s.replace(w, "")
    # 去掉邮箱、电话、证书编号
    s = re.sub(r"[\w.]+@[\w.]+", "", s)
    s = re.sub(r"\d{3,4}-\d{7,8}", "", s)
    s = re.sub(r"S\d{10,}", "", s)
    # 剔除混入的分析师/联系人行
    s = re.sub(r"联系人[:：].*", "", s)
    s = re.sub(r"分析师[:：].*", "", s)
    # 剔除孤立标点残留
    s = s.replace("·", "").strip()
    return s

# 财务表/页脚污染锚点：一旦碰到即截断
FINANCE_ANCHORS = [
    "营业收入(百万元)", "净利润(百万元)", "(+/-%)", "每股收益（元）",
    "EBITMargin", "净资产收益率", "市盈率（PE）", "市净率（PB）",
    "EV/EBITDA", "2024，2025", "2024 2025", "盈利预测和财务指标",
    "2026E，2027E", "资料来源：Wind", "：Wind、预测", "正文之后的免责声明",
    "相关研究报告", "《", "——20", "证券研究报告",
    "百万元", "同比（%）", "东吴证券研究所", "证券研究所", "执业证书",
    "归母净利润（百万元）", "营业总收入（百万元）", "股价走势", "市场数据",
    "Table", "table", "TTa", "EPS]", "P/E（现价）",
    "市场数据", "收盘价", "市净率", "流通A股市值", "一年最低", "总市值(百万元)",
]

def truncate_finance(s: str) -> str:
    """遇到财务表/页脚/旧报告标题污染即截断，并丢弃尾随的无中文残片。"""
    for a in FINANCE_ANCHORS:
        idx = s.find(a)
        if idx > 0:
            s = s[:idx]
    # 丢弃尾随的"无中文字符"残片（表格数字/页脚碎片被误并入）
    s = re.sub(r"[，,。、\s]*[\d./%+\-()（）\s]+$", "", s)
    return s.rstrip("，。、 ")

def extract_rating(text: str) -> str:
    # 首页评级如 "优于大市(维持)" 或 "买入(维持)"
    m = re.search(r"(买入|增持|推荐|强烈推荐|优于大市|中性|减持|卖出|谨慎推荐|持有)\s*[（(]([^）)]*)[）)]", text)
    if m:
        return f"{m.group(1)}({m.group(2)})"
    m = re.search(r"维持[“\"]([^”\"]+)[”\"]评级", text)
    if m:
        return m.group(1)
    m = re.search(r"(买入|增持|推荐|强烈推荐|优于大市|中性|减持|卖出|谨慎推荐|持有)", text)
    return m.group(1) if m else ""

def extract_forecast(text: str) -> str:
    # "归母净利润至 2.5/2.7/3.0 亿元，对应 PE 为 21/18/16 倍"
    m = re.search(r"归母净利润[至到]?\s*([\d./]+\s*亿元)[，,]\s*对应\s*PE\s*[为是]?\s*([\d./]+\s*倍)", text)
    if m:
        return f"预计归母净利润 {m.group(1)}，对应 PE {m.group(2)}"
    m = re.search(r"归母净利润[至到]?\s*([\d./]+\s*亿元)", text)
    if m:
        return f"预计归母净利润 {m.group(1)}"
    return ""

# 子句级垃圾碎片：含这些词的子句直接丢弃（分析师名/评级/股价/旧报告标题等）
BAD_FRAG = ["分析师", "研究员", "（维持）", "证券", "《", "股价", "元；",
            "2024 2025", "2026E", "2027E", "2028E", "20242025", "联系方式",
            "执业证书", "研究所", "评级：", "评级:"]

def _clean_sentences(raw: str) -> str:
    """按句切分，丢弃无中文残片与含垃圾碎片的子句。"""
    raw = strip_noise(raw)
    raw = re.sub(r"\s+", "", raw)
    segs = re.split(r"[；;。\n]", raw)
    kept = []
    for s in segs:
        if not s:
            continue
        if not re.search(r"[\u4e00-\u9fff]", s):
            if kept:
                continue
        if any(b in s for b in BAD_FRAG):
            continue
        kept.append(s)
    out = "；".join(kept)
    return truncate_finance(out).rstrip("，。、 ")

# 风险/建议段的终止锚（遇到即截断，不吞入正文图表/财务表/免责声明）
SECTION_END = r"(?:投资建议[：:]|风险提示[：:]|图表|图\d|表\d|资料来源|免责|在任何情况|盈利预测和财务指标|财务预测与估值|资产负债表|相关研究报告|评级说明|披露声明)"

def extract_risk(text: str) -> str:
    m = re.search(r"风险提示[：:]\s*(.+?)(?=" + SECTION_END + r"|\Z)", text, re.S)
    if m:
        return _clean_sentences(m.group(1))
    return ""

DISCLAIMER_KW = ["责任", "谨慎", "版权", "许可", "翻版", "退回并销毁", "普通投资者"]

def extract_advice(text: str) -> str:
    m = re.search(r"投资建议[：:]\s*(.+?)(?=" + SECTION_END + r"|\Z)", text, re.S)
    if m:
        s = _clean_sentences(m.group(1))
        if any(k in s for k in DISCLAIMER_KW):
            return ""  # 实为免责声明，丢弃
        return s
    return ""

# 侧栏/表格噪声词：出现在句子里即判定为非正文（市场数据、收盘价等）
SIDEBAR_NOISE = ["市场数据", "收盘价", "市净率", "流通A股市值", "一年最低",
                 "总市值", "股价走势", "沪深300", "执业证书", "证券研究报告",
                 "盈利预测与估值", "营业总收入（百万元）", "归母净利润（百万元）",
                 "(元)", "（元）", "EPS-最新摊薄"]

def extract_core(text: str) -> str:
    """核心观点：抓 '核心观点/投资要点/投资评级/内容摘要/摘要' 段，
    按 ◼ 项目符号切分，丢弃混入的侧栏/表格噪声句，拼接业务实质内容。"""
    anchor = r"(?:核心观点|投资要点|投资评级|内容摘要|摘要)\s*"
    m = re.search(anchor + r"(.+?)(?:\n风险提示[：:]|\n投资建议[：:]|\n财务预测|\n图\d|\n表\d|盈利[预测与估]|\Z)", text, re.S)
    raw = m.group(1) if m else ""
    if not raw.strip():
        m2 = re.search(r"◼\s*(.+?)(?:\n◼|\n风险提示[：:]|\Z)", text, re.S)
        raw = m2.group(1) if m2 else text[:800]
    # 按 ◼ / 换行 分句
    parts = re.split(r"◼|\n", raw)
    kept = []
    for p in parts:
        p = strip_noise(p)
        p = re.sub(r"\s+", "", p)
        if not p:
            continue
        if any(w in p for w in SIDEBAR_NOISE):
            continue
        if not re.search(r"[\u4e00-\u9fff]", p):  # 无中文，丢弃
            continue
        kept.append(p)
    out = "；".join(kept)
    out = truncate_finance(out)
    return out[:500].strip()

def parse_note(path: Path) -> dict:
    t = path.read_text(encoding="utf-8")
    fm = {}
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", t, re.S)
    if not m:
        return {}
    for line in m.group(1).splitlines():
        kv = re.match(r'(\w+):\s*(.*)$', line)
        if kv:
            v = kv.group(2).strip()
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            fm[kv.group(1)] = v
    return fm

def backfill_note(stem: str, extracted: dict):
    """把抽取结果写回笔记：frontmatter 补 rating/forecast，正文补核心/风险/建议章节。"""
    fpath = REAL / f"{stem}.md"
    if not fpath.exists():
        return False
    text = fpath.read_text(encoding="utf-8")
    fm, body = {}, text
    mm = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if mm:
        fm_raw, body = mm.group(1), mm.group(2)
        for line in fm_raw.splitlines():
            kv = re.match(r'(\w+):\s*(.*)$', line)
            if kv:
                v = kv.group(2).strip()
                if v.startswith('"') and v.endswith('"'):
                    v = v[1:-1]
                fm[kv.group(1)] = v

    # 更新 frontmatter 字段
    if extracted.get("rating"):
        fm["rating"] = extracted["rating"]
    if extracted.get("forecast"):
        fm["forecast"] = extracted["forecast"]

    # 重建 frontmatter 文本
    fm_lines = ["---"]
    for k in ["tags", "org", "declareDate", "title", "concept", "rating",
              "industry", "object", "analyst", "source", "pdfUrl", "pdfAvailable", "forecast"]:
        if k in fm and fm[k] != "":
            v = fm[k]
            if k in ("tags",):
                fm_lines.append(f"tags: {v}")
            elif any(c in v for c in [":", "/", "（", "）", " "]) or k in ("title", "org", "concept", "industry", "object", "analyst", "source", "pdfUrl"):
                fm_lines.append(f'{k}: "{v}"')
            else:
                fm_lines.append(f"{k}: {v}")
    fm_block = "\n".join(fm_lines) + "\n"

    # 重建正文：保留标题 + 来源 callout + 交叉引用；插入/更新核心观点/风险/建议
    # 先分离「来源 callout」「交叉引用」「分隔线+脚注」
    callout_m = re.search(r"(> \[!note\][\s\S]*?)(?=\n## 知识库交叉引用|\Z)", body)
    callout = callout_m.group(1).strip() if callout_m else ""
    # 保留原笔记已有的「知识库交叉引用」完整块（含概念卡片+逆检索板块链接，
    # 由 _gen_obsidian.py 回填），切勿重写覆盖。仅在缺失时生成最小占位。
    xref_m = re.search(r"(## 知识库交叉引用[\s\S]*?)(?=\n---|\Z)", body)
    if xref_m:
        xref = xref_m.group(1).strip()
    else:
        card = "概念卡片/" + fm.get("concept", "").replace("/", "·")
        xref = f"## 知识库交叉引用\n\n- 概念归类：[[{card}]]"
    footer_m = re.search(r"(\n---[\s\S]*)$", body)
    footer = footer_m.group(1).strip() if footer_m else ""

    new_body = [f"# {fm.get('title','')}", "", callout, ""]
    if extracted.get("core"):
        new_body += ["## 核心观点", "", extracted["core"], ""]
    if extracted.get("forecast"):
        new_body += ["## 盈利预测", "", extracted["forecast"], ""]
    if extracted.get("advice"):
        new_body += ["## 投资建议", "", extracted["advice"], ""]
    if extracted.get("risk"):
        new_body += ["## 风险因素", "", extracted["risk"], ""]
    new_body += [xref, "", footer]

    fpath.write_text(fm_block + "\n" + "\n".join(new_body).rstrip() + "\n", encoding="utf-8")
    return True

def process_one(stem: str, url: str, force: bool = False) -> dict:
    cache_pdf = CACHE / f"{stem}.pdf"
    if not cache_pdf.exists() or force:
        data = download_pdf(url)
        if not data:
            return {"stem": stem, "ok": False, "reason": "download_failed"}
        cache_pdf.write_bytes(data)
    try:
        text = pdf_to_text(cache_pdf.read_bytes())
    except Exception as e:
        return {"stem": stem, "ok": False, "reason": f"parse_err:{e}"}
    ext = {
        "core": extract_core(text),
        "rating": extract_rating(text),
        "forecast": extract_forecast(text),
        "advice": extract_advice(text),
        "risk": extract_risk(text),
    }
    backfill_note(stem, ext)
    ext["ok"] = True
    return ext

def process_all(limit: int = 0, force: bool = False) -> dict:
    """批量抽取全部研报 PDF 内容回填笔记。幂等：已含『## 核心观点』的跳过。"""
    import re as _re
    stats = {"done": 0, "skip": 0, "fail": 0, "total": 0}
    targets = []
    for f in sorted(REAL.glob("研报_*.md")):
        t = f.read_text(encoding="utf-8", errors="ignore")
        if not force and "## 核心观点" in t:
            stats["skip"] += 1
            continue
        mu = _re.search(r'pdfUrl:\s*"([^"]+)"', t)
        if not mu or not mu.group(1):
            stats["skip"] += 1
            continue
        targets.append((f.stem, mu.group(1)))
    stats["total"] = len(targets)
    for i, (stem, url) in enumerate(targets, 1):
        try:
            r = process_one(stem, url, force=force)
            if r.get("ok"):
                stats["done"] += 1
            else:
                stats["fail"] += 1
                print(f"  [FAIL] {stem}: {r.get('reason')}")
        except Exception as e:
            stats["fail"] += 1
            print(f"  [ERR] {stem}: {e}")
        if limit and i >= limit:
            break
    return stats

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        force = "--force" in sys.argv
        limit = 0
        for j, a in enumerate(sys.argv):
            if a.startswith("--limit="):
                limit = int(a.split("=")[1])
        st = process_all(limit=limit, force=force)
        print("批量抽取完成:", json.dumps(st, ensure_ascii=False))
    else:
        # 测试单篇
        test_stem = "研报_20260813_001"
        test_url = "https://pdf.dfcfw.com/pdf/H3_AP202608131827933066_1.pdf"
        if len(sys.argv) > 2:
            test_stem, test_url = sys.argv[1], sys.argv[2]
        r = process_one(test_stem, test_url)
        print(json.dumps(r, ensure_ascii=False, indent=2))
