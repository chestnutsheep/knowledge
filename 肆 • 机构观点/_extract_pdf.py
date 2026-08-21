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

def _page_text(page) -> str:
    """提取单页文本；双栏/侧栏页优先保留正文列，减少行情侧栏串入。"""
    words = page.extract_words(x_tolerance=2, y_tolerance=3, keep_blank_chars=False)
    if not words:
        return page.extract_text(layout=True) or page.extract_text() or ""
    lines = []
    for word in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if lines and abs(word["top"] - lines[-1]["top"]) <= 3:
            lines[-1]["words"].append(word)
        else:
            lines.append({"top": word["top"], "words": [word]})
    clusters = []
    for line in lines:
        ws = sorted(line["words"], key=lambda w: w["x0"])
        groups = []
        for w in ws:
            if groups and w["x0"] - groups[-1][-1]["x1"] <= 18:
                groups[-1].append(w)
            else:
                groups.append([w])
        for group in groups:
            text = "".join(w["text"] for w in group).strip()
            if text:
                clusters.append((line["top"], group[0]["x0"], group[-1]["x1"], text))
    width = float(page.width)
    sidebar_re = re.compile(
        r"市场数据|当前价格|52周|总市值|流通市值|总股本|流通股|近一月换手|股价走势|"
        r"主要股东|A股数|A市值|机构投资者|产品组合|证券分析师|执业证书|邮箱|近期评等|"
        r"股价涨跌|股价12个月|上证指数|沪深300|公司基本资讯|产业别|基础数据|相关研究|"
        r"图表|股价表现|公司基本资料"
    )
    sidebar = [c for c in clusters if sidebar_re.search(c[3])]
    if sidebar:
        sidebar_x = [c[1] for c in sidebar]
        median_x = sorted(sidebar_x)[len(sidebar_x) // 2]
        # 仅当侧栏明显位于页面边缘，且正文列确实存在时才裁剪。
        body_candidates = [c for c in clusters if len(c[3]) >= 20]
        if median_x < width * .35 and any(c[1] > width * .35 for c in body_candidates):
            cutoff = max(c[2] for c in sidebar) + 12
            clusters = [c for c in clusters if c[1] >= cutoff]
        elif median_x > width * .65 and any(c[2] < width * .65 for c in body_candidates):
            cutoff = min(c[1] for c in sidebar) - 12
            clusters = [c for c in clusters if c[2] <= cutoff]
        # 右栏数字/图表经常没有关键词，按已识别侧栏的空间位置一并剔除。
        if median_x > width * .55:
            right_cutoff = min(c[1] for c in sidebar) - 8
            clusters = [c for c in clusters if c[1] < right_cutoff]
        # 同一行可能被拆成多个文字块；即使未达到 cutoff，也丢弃明确的侧栏块。
        clusters = [c for c in clusters if not sidebar_re.search(c[3])]
    result = "\n".join(t for _, _, _, t in sorted(clusters, key=lambda c: (c[0], c[1])))
    # 复杂表格页可能被误裁剪；保留原始文本作为降级输入，不让整页消失。
    if len(result) < 80:
        return page.extract_text(layout=True) or page.extract_text() or result
    return result


def pdf_to_text(pdf_bytes: bytes) -> str:
    import io
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        return "\n".join(_page_text(pg) for pg in pdf.pages)

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
    # 首页评级如 "优于大市(维持)" 或 "买入(维持)"；PDF 换行不应进入字段。
    compact = re.sub(r"\s+", "", text)
    m = re.search(r"(买入|增持|推荐|强烈推荐|优于大市|中性|减持|卖出|谨慎推荐|持有)[（(]([^）)]*)[）)]", compact)
    if m:
        return f"{m.group(1)}({m.group(2)})"
    m = re.search(r"维持[“\"]([^”\"]+)[”\"]评级", compact)
    if m:
        return m.group(1)
    m = re.search(r"(买入|增持|推荐|强烈推荐|优于大市|中性|减持|卖出|谨慎推荐|持有)", compact)
    return m.group(1) if m else ""

def extract_forecast(text: str) -> str:
    """只从“盈利预测/投资评级”段提取预测，避免误抓实际利润。"""
    section = text
    m_section = re.search(
        r"(?:盈利预测与投资评级|盈利预测及投资评级|盈利预测)\s*[：:]?(.*?)(?=\n\s*(?:风险提示|风险因素)|\Z)",
        text, re.S,
    )
    if m_section:
        section = m_section.group(1)
    compact = re.sub(r"\s+", "", section)
    # 常见表述：预计 2026-2028 年归母净利润分别为 38、48、51 亿元。
    m = re.search(r"(?:归母净利润|归母净利).*?(?:分别为|分为|为)\s*([\d、,./]+)\s*亿元", compact)
    if m:
        nums = m.group(1).replace(",", "、").replace("/", "、")
        return f"预计归母净利润 {nums} 亿元"
    m = re.search(r"归母净利润[至到]\s*([\d./]+\s*亿元).*?对应PE[为是]?\s*([\d./]+\s*倍)", compact)
    if m:
        return f"预计归母净利润 {m.group(1)}，对应 PE {m.group(2)}"
    # 只有明确“预计”时才允许单值兜底，避免抓到“实现归母净利润”。
    m = re.search(r"预计(?:公司)?(?:将实现)?归母净利润\s*([\d.]+\s*亿元)", compact)
    return f"预计归母净利润 {m.group(1)}" if m else ""

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

DISCLAIMER_KW = [
    "本报告", "本公司", "本报告信息均来源于", "市场有风险", "投资需谨慎",
    "评级标准", "评级说明", "分析师承诺", "版权归", "未经书面许可",
    "未经许可", "不得以任何方式", "客户使用", "风险自担", "退回并销毁",
]

# 一旦出现这些词，后续通常是评级定义、免责声明或财务表，不再写入正文。
DISCLAIMER_RE = re.compile(
    r"(?:本报告信息均来源于|本报告仅供|本公司不会因|市场有风险|投资需谨慎|"
    r"投资评级说明|评级标准|评级说明|分析师承诺|免责声明|版权归|未经.{0,12}许可|"
    r"不得以任何方式|请务必阅读.{0,12}免责|风险自担|年度截止|【投资评等说明】|"
    r"东吴证券研究所|国信证券经济研究所|太平洋证券股份有限公司)"
)


def _cut_disclaimer(s: str) -> str:
    m = DISCLAIMER_RE.search(s)
    return s[:m.start()] if m else s


def _is_noise_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if any(w in s for w in SIDEBAR_NOISE):
        return True
    if any(w in s for w in ("证券研究所", "证券分析师", "执业证书", "联系方式", "Compa ny", "Ch in a Re sea", "点评报告")):
        return True
    if s in {"•", "-", "—", "·"}:
        return True
    if re.fullmatch(r"[\d\s./%+\-()（）亿元万股A-Za-z|]+", s):
        return True
    # 行情图坐标、表格列标题、连续日期串
    if len(re.findall(r"20\d{2}", s)) >= 2 and re.search(r"20\d{2}[/年\-]", s):
        return True
    if re.search(r"(?:A股数|流通股|总市值|收盘价|一年最低|个股表现|主要股东|近一月换手|股价涨跌)", s):
        return True
    if re.search(r"(?:预测指标|年度截止|营业收入.*百万元|归母净利.*百万元|每股收益.*元|"
                 r"基\s*础数据|每\s*股净资产|资产负债率|总\s*股本|流\s*通A股|"
                 r"相关研究|特别声明|附录|损益表|资产负债表|现金流量表)", s):
        return True
    return False


def _normalize_section(raw: str, max_chars: int = 1800) -> str:
    raw = _cut_disclaimer(raw)
    raw = raw.replace("", "\n• ").replace("◼", "\n• ")
    lines = []
    for line in raw.splitlines():
        line = strip_noise(line)
        line = re.sub(r"\s+", " ", line).strip()
        # 页脚常与正文粘在同一行，先截断再判断噪声。
        line = re.split(r"请认真阅读(?:正文之后|文后)的?免责声明?条款?", line)[0].strip()
        line = re.split(r"(?:资料来源|数据来源)[:：]", line)[0].strip()
        if _is_noise_line(line):
            continue
        if line:
            lines.append(line)
    if not lines:
        return ""
    # PDF 换行通常只是排版换行：中文相邻行直接合并，项目符号单独成段。
    paragraphs = []
    current = ""
    for line in lines:
        if line.startswith("•"):
            if current:
                paragraphs.append(current)
            current = line[1:].strip()
            if not current:
                continue
        elif not current:
            current = line
        elif current.endswith(("。", "！", "？", ";", "；")):
            paragraphs.append(current)
            current = line
        else:
            current += line if (current[-1] >= "\u4e00" and line[0] >= "\u4e00") else " " + line
    if current:
        paragraphs.append(current)
    out = "\n\n".join(p.strip() for p in paragraphs if p.strip())
    out = re.sub(r"[；;]{2,}", "；", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    # 删除常见的侧栏碎片被插入正文后的残留。
    out = re.sub(r"\d{4}年\d{1,2}月\d{1,2}日", "", out)
    out = re.sub(r"(?:当前价格|52周价格区间|总市值|流通市值|总股本|流通股|近一月换手)[^\n]{0,35}", "", out)
    out = re.sub(r"\(?百万元\)?\s*[\d,.]+", "", out)
    out = re.sub(r"(?:分析师|执业证书编号|邮箱)[:：]?[^\n]*", "", out)
    out = re.sub(r"(?:基础数据|基\s*础数据|相关研究|图表|股价表现|公司基本资料)[^\n]*", "", out)
    out = re.sub(r"^\s*[:：]\s*", "", out)
    out = re.sub(r"\s+(?:基础数据|基\s*础数据|每\s*股净资产|资产负债率|总\s*股本|流\s*通A股)\b.*", "", out)
    out = re.sub(r"较s年初", "较年初", out)
    out = re.sub(r"(?<=[\u4e00-\u9fff])s(?=年)", "", out)
    out = re.sub(r"(?:2025/\d{1,2}/\d{1,2}){2,}", "", out)
    out = re.sub(r"(?:20\d{2}/){2,}20\d{2}/\d{1,2}/\d{1,2}", "", out)
    # 不写入明显半句；允许最后是数字/单位，但不能是连接词。
    if re.search(r"(?:公司下|其中|并且|以及|将|因而|因此|从而|在)$", out):
        out = re.sub(r"[^。！？；]*$", "", out).rstrip("，、 ")
    # 截断后的结果不能以明显的悬空连接词或页脚词结束。
    out = re.sub(r"(?:公司下|一阶段业|研究所|分析师|邮箱|点评报告|[•·])$", "", out).rstrip("，、；; ")
    if len(out) > max_chars:
        # 在完整句/分号边界截断，避免把句子截成半句。
        boundary = max(out.rfind("。", 0, max_chars), out.rfind("；", 0, max_chars))
        out = out[:boundary + 1] if boundary >= max_chars // 2 else out[:max_chars]
    return out.rstrip("，、；; ")


def extract_risk(text: str) -> str:
    m = re.search(r"(?:风险提示|风险因素)[：:]?\s*(.+?)(?="
                  r"(?:盈利预测|财务预测|图\s*\d|表\s*\d|资料来源|免责声明|"
                  r"投资评级说明|评级标准|请务必阅读|附录|三张报表|损益表|"
                  r"资产负债表|现金流量表|特别声明|公司点评附录)|\Z)", text, re.S)
    return _normalize_section(m.group(1), 900) if m else ""


def extract_advice(text: str) -> str:
    # 优先正文中的投资建议；不把免责声明中出现的“投资建议”当作建议。
    patterns = [
        r"(?:^|\n)\s*投资建议[：:]\s*(.+?)(?=(?:\n|风险提示|盈利预测|财务预测|图\s*\d|表\s*\d)|\Z)",
        r"(?:^|\n)\s*盈利预测及投资评级[：:]?\s*(.+?)(?=(?:\n|风险提示|盈利预测|财务预测|图\s*\d|表\s*\d)|\Z)",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text, re.S):
            s = _normalize_section(m.group(1), 1000)
            if not s or any(k in s for k in DISCLAIMER_KW) or len(s) < 18:
                continue
            # 过滤明显从段中间开始的残句，宁可不填。
            if re.match(r"^(?:别为|利为|为|分别为|的|领)", s):
                continue
            if not re.search(r"[。！？；]$", s):
                # 允许 PDF 没有句号，但必须有完整评级/盈利结论。
                if not re.search(r"(?:评级|建议|买入|增持|持有|卖出|回避)[”）)]?$", s):
                    continue
            return s
    return ""

# 侧栏/表格噪声词：出现在句子里即判定为非正文（市场数据、收盘价等）
SIDEBAR_NOISE = ["市场数据", "收盘价", "市净率", "流通A股市值", "一年最低",
                 "总市值", "股价走势", "沪深300", "执业证书", "证券研究报告",
                 "盈利预测与估值", "营业总收入（百万元）", "归母净利润（百万元）",
                 "(元)", "（元）", "EPS-最新摊薄"]

def extract_core(text: str) -> str:
    """抽取明确的投资要点块；遇到财务预测/风险提示等项目符号时停止。"""
    headings = ["核心观点", "投资要点", "内容摘要", "摘要", "观点"]
    stop = r"(?:风险提示|风险因素|投资建议|盈利预测与投资评级|盈利预测和财务指标|财务预测与估值|财务预测|图\s*\d|表\s*\d)"
    candidates = []
    for heading in headings:
        # 允许标题后有右侧图表百分比行；必须捕获到正文项目符号。
        pattern = (r"(?:^|\n)\s*" + re.escape(heading) +
                   r"\s*(?:[^\n]*\n){0,5}?\s*(?:[◼•]\s*)?(.+?)" +
                   r"(?=\n\s*[◼•]\s*(?:" + stop + r")|\n\s*(?:" + stop + r")|\Z)")
        for m in re.finditer(pattern, text, re.S):
            cleaned = _normalize_section(m.group(1), 1800)
            if len(cleaned) >= 35:
                candidates.append(cleaned)
    if not candidates:
        return ""
    business = ("公司", "业绩", "收入", "利润", "产量", "需求", "订单", "项目", "产品", "产能")
    candidates.sort(key=lambda s: (sum(w in s for w in business), min(len(s), 1800)), reverse=True)
    result = candidates[0]
    # 页面取词可能把“盈利预测与投资评级”粘在上一行，按内联锚点再次截断。
    inline_stop = re.search(r"(?:盈利预测(?:与|及)投资评级|盈利预测和财务指标|风险提示|风险因素)", result)
    if inline_stop:
        result = result[:inline_stop.start()].rstrip("，、；; ")
    result = re.sub(r"(?:盈利预测(?:与|及)投资评级|盈利预测和财务指标)[：:]?\s*", "", result)
    result = result.lstrip("：:，,；; ")
    if any(w in result for w in ("A股数", "损益表", "资产负债表", "现金流量表", "个股表现", "股价涨跌", "主要股东", "市场数据", "流通股市值", "分析师", "评级说明", "免责声明")):
        return ""
    return result

def split_note(text: str):
    """解析正常或历史损坏的笔记，兼容缺少结尾 --- 的 frontmatter。"""
    if not text.startswith("---"):
        return None
    rest = text[3:].lstrip("\n")
    marker = re.search(r"(?m)^---[ \t]*$", rest)
    heading = re.search(r"(?m)^#\s", rest)
    # 损坏旧笔记没有 frontmatter 结束符，但正文末尾有脚注 ---；
    # 必须优先取正文标题之前的边界，不能把脚注分隔线误当成 frontmatter 结束符。
    if heading and (not marker or heading.start() < marker.start()):
        return rest[:heading.start()].rstrip("\n"), rest[heading.start():].lstrip("\n")
    if marker:
        return rest[:marker.start()].rstrip("\n"), rest[marker.end():].lstrip("\n")
    return None


def _quote_yaml_value(value: str) -> str:
    value = str(value).replace('"', '\\"')
    return f'"{value}"'


def update_frontmatter(fm_raw: str, updates: dict) -> str:
    """只更新指定字段，保留未知字段，并移除已知的孤立 YAML 延续行。"""
    lines = fm_raw.splitlines()
    seen = set()
    out = []
    previous_key = ""
    for line in lines:
        m = re.match(r"^([A-Za-z_][\w-]*):(?:\s*)(.*)$", line)
        if not m:
            # 兼容历史损坏的 rating: "增持"\n持"；不把孤立延续行带回去。
            if previous_key in {"rating", "forecast"} and re.fullmatch(r"[^:\n]+[\"']", line.strip()):
                continue
            out.append(line)
            continue
        previous_key = m.group(1)
        if m.group(1) not in updates:
            out.append(line)
            continue
        key = m.group(1)
        value = updates[key]
        out.append(f"{key}: {_quote_yaml_value(value)}")
        seen.add(key)
    for key, value in updates.items():
        if key not in seen and value not in (None, ""):
            out.append(f"{key}: {_quote_yaml_value(value)}")
    return "---\n" + "\n".join(out).rstrip() + "\n---\n"


def clean_section_text(value: str, heading: str = "") -> str:
    """清除 PDF 双栏串列、页眉页脚和表格碎片，保持正文段落。"""
    if not value:
        return ""
    value = value.replace("\uf075", "•").replace("\uf0be", "•").replace("\uf06c", "•")
    value = value.replace("➢", "• ")
    value = value.replace("扣扣非", "扣非").replace("非后归母", "扣非后归母").replace("营业比", "营业收入同比")
    value = re.sub(r"(?m)^\s*\[Table_[^\]]+\]\s*$", "", value)
    value = re.sub(r"(?:Table[_ ]*Author|Table[_ ]*A?uthor|分析师|执业证号|联系电话|联系方式|邮箱)[:：]?[^。；\n]*", "", value, flags=re.I)
    value = re.sub(r"最高价/最低价[^。；\n]*", "", value)
    value = re.sub(r"(?:12个月价格区间|交易数据|日均成交额)[^。；\n]*", "", value)
    value = re.sub(r"(?:数据来源|资料来源)[:：]?\s*Wind", "", value, flags=re.I)
    value = re.sub(r"优于大市\s*[（(]维持[）)]", "", value)
    value = re.sub(r"/\s*[\d,./]+\s*百万元", "", value)
    value = re.sub(r"\s*水\s*：\s*Wind", "", value, flags=re.I)
    value = re.sub(r"(?:基础数据|基\s*础数据|相关研究|公司基本资料|股价表现)[^。；\n]*", "", value)
    value = re.sub(r"[ \t]+", " ", value)
    paragraphs = []
    for paragraph in re.split(r"\n\s*\n", value):
        paragraph = paragraph.strip(" \n；;，,")
        if not paragraph or paragraph in {"•", "-", "—", "·"}:
            continue
        # 明显整行财务表/行情表不属于核心观点。
        digits = len(re.findall(r"\d", paragraph))
        if ("百万元" in paragraph and digits >= 8) or any(x in paragraph for x in ("损益表", "资产负债表", "现金流量表")):
            continue
        if re.search(r"(?:研究所|证券分析师|执业证书|Table[_ ]*Author)", paragraph, re.I):
            continue
        paragraph = re.sub(r"^\s*[^。；\n]{0,24}[：:]\s*", "", paragraph) if heading == "核心观点" and "：" in paragraph[:35] else paragraph
        paragraph = re.sub(r"\s{2,}", " ", paragraph).strip()
        if paragraph:
            paragraphs.append(paragraph)
    result = "\n\n".join(paragraphs)
    result = re.sub(r"盈利预测(?:与|及)投资评级[：:]?.*$", "", result, flags=re.S)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip(" \n；;，,")


def update_body_sections(body: str, extracted: dict) -> str:
    """局部更新自动章节，保留未知章节、人工内容、交叉引用和页脚。"""
    headings = ["核心观点", "盈利预测", "投资建议", "风险因素"]
    available = {h: clean_section_text(extracted.get({"核心观点": "core", "盈利预测": "forecast", "投资建议": "advice", "风险因素": "risk"}[h], ""), h) for h in headings}
    section_re = re.compile(r"(?m)^##[ \t]+(核心观点|盈利预测|投资建议|风险因素)[ \t]*$")
    matches = list(section_re.finditer(body))
    replacements = []
    for i, match in enumerate(matches):
        heading = match.group(1)
        value = available.get(heading, "")
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        # 自动章节的边界不能越过任意二级标题、交叉引用或文末脚注。
        tail = body[match.end():]
        boundaries = []
        next_h2 = re.search(r"(?m)^##\s+", tail)
        if next_h2:
            boundaries.append(match.end() + next_h2.start())
        footer = re.search(r"(?m)^---\s*$", tail)
        if footer:
            boundaries.append(match.end() + footer.start())
        if boundaries:
            end = min(end, *boundaries)
        if value:
            replacements.append((match.start(), end, f"## {heading}\n\n{value.strip()}\n\n"))
        else:
            # 没有可信新结果时保留原章节，避免误删用户手工补充。
            continue
    result = body
    for start, end, replacement in reversed(replacements):
        result = result[:start] + replacement + result[end:]
    # 尚不存在的可信章节插入交叉引用之前；空结果不制造占位章节。
    missing = [h for h in headings if available[h] and not re.search(rf"(?m)^##\s+{re.escape(h)}\s*$", result)]
    if missing:
        insert = "\n".join(f"## {h}\n\n{available[h].strip()}\n" for h in missing)
        xref = re.search(r"(?m)^##\s+知识库交叉引用\s*$", result)
        footer = re.search(r"(?m)^---\s*$", result)
        positions = [m.start() for m in (xref, footer) if m]
        pos = min(positions) if positions else len(result)
        result = result[:pos].rstrip() + "\n\n" + insert.rstrip() + "\n\n" + result[pos:].lstrip()
    return result.strip()


def sanitize_existing_notes(dry_run: bool = False) -> dict:
    """只净化既有自动章节与 frontmatter，不重抽取、不修改其他章节。"""
    stats = {"done": 0, "unchanged": 0, "bad": 0, "dry_run": dry_run}
    section_re = re.compile(r"(?ms)^(##[ \t]+(核心观点|盈利预测|投资建议|风险因素)[ \t]*$)\n*(.*?)(?=^##[ \t]+|^---[ \t]*$|\Z)")
    for path in sorted(REAL.glob("研报_*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        parsed = split_note(text)
        if not parsed:
            stats["bad"] += 1
            continue
        fm_raw, body = parsed
        def repl(match):
            cleaned = clean_section_text(match.group(3), match.group(2))
            return f"{match.group(1)}\n\n{cleaned}\n\n" if cleaned else ""
        new_body = section_re.sub(repl, body).strip()
        candidate = update_frontmatter(fm_raw, {}) + "\n" + new_body + "\n"
        if candidate == text:
            stats["unchanged"] += 1
            continue
        if not split_note(candidate) or not re.search(r"(?m)^#\s+\S", split_note(candidate)[1]):
            stats["bad"] += 1
            continue
        stats["done"] += 1
        if not dry_run:
            tmp = path.with_suffix(".md.tmp")
            tmp.write_text(candidate, encoding="utf-8")
            tmp.replace(path)
    return stats


def parse_note(path: Path) -> dict:
    parsed = split_note(path.read_text(encoding="utf-8"))
    if not parsed:
        return {}
    fm_raw, _ = parsed
    fm = {}
    for line in fm_raw.splitlines():
        kv = re.match(r'(\w+):\s*(.*)$', line)
        if kv:
            v = kv.group(2).strip()
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            fm[kv.group(1)] = v
    return fm

def backfill_note(stem: str, extracted: dict):
    """安全回写：只改 frontmatter 的抽取字段和自动章节，保留其余内容。"""
    fpath = REAL / f"{stem}.md"
    if not fpath.exists():
        return False
    text = fpath.read_text(encoding="utf-8")
    parsed = split_note(text)
    if not parsed:
        return False
    fm_raw, body = parsed
    updates = {}
    if extracted.get("rating"):
        updates["rating"] = extracted["rating"]
    if extracted.get("forecast"):
        updates["forecast"] = extracted["forecast"]
    fm_block = update_frontmatter(fm_raw, updates)
    new_body = update_body_sections(body, extracted)
    candidate = fm_block + "\n" + new_body.rstrip() + "\n"
    # 写入前做结构校验，防止再次制造不可解析笔记。
    check = split_note(candidate)
    if not check or not re.search(r"(?m)^#\s+", check[1]):
        return False
    tmp = fpath.with_suffix(".md.tmp")
    tmp.write_text(candidate, encoding="utf-8")
    tmp.replace(fpath)
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

def process_cached(limit: int = 0, dry_run: bool = False) -> dict:
    """只重解析本地缓存 PDF，修复历史污染；不下载、不触碰无缓存的新笔记。"""
    stats = {"done": 0, "skip": 0, "fail": 0, "total": 0, "with_core": 0, "dry_run": dry_run}
    targets = []
    for pdf in sorted(CACHE.glob("研报_*.pdf")):
        note = REAL / f"{pdf.stem}.md"
        if note.exists():
            targets.append(pdf.stem)
    stats["total"] = len(targets)
    for i, stem in enumerate(targets, 1):
        try:
            text = pdf_to_text((CACHE / f"{stem}.pdf").read_bytes())
            ext = {
                "core": extract_core(text),
                "rating": extract_rating(text),
                "forecast": extract_forecast(text),
                "advice": extract_advice(text),
                "risk": extract_risk(text),
            }
            # 只写有至少一个可信字段的结果；空结果不破坏原笔记。
            if any(ext.get(k) for k in ("core", "forecast", "advice", "risk")):
                if dry_run:
                    stats["done"] += 1
                    stats["with_core"] += bool(ext.get("core"))
                    if stats["done"] <= 5:
                        print(f"  [DRY] {stem}: core={len(ext['core'])} forecast={len(ext['forecast'])} advice={len(ext['advice'])} risk={len(ext['risk'])}")
                elif backfill_note(stem, ext):
                    stats["done"] += 1
                    stats["with_core"] += bool(ext.get("core"))
                else:
                    stats["skip"] += 1
            else:
                stats["skip"] += 1
        except Exception as e:
            stats["fail"] += 1
            print(f"  [ERR] {stem}: {e}")
        if limit and i >= limit:
            break
    return stats


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
    if len(sys.argv) > 1 and sys.argv[1] == "sanitize":
        st = sanitize_existing_notes(dry_run="--dry-run" in sys.argv)
        print("既有章节净化完成:", json.dumps(st, ensure_ascii=False))
    elif len(sys.argv) > 1 and sys.argv[1] == "cached":
        limit = 0
        dry_run = "--dry-run" in sys.argv
        for j, a in enumerate(sys.argv):
            if a.startswith("--limit="):
                limit = int(a.split("=")[1])
        st = process_cached(limit=limit, dry_run=dry_run)
        print("本地缓存修复完成:", json.dumps(st, ensure_ascii=False))
    elif len(sys.argv) > 1 and sys.argv[1] == "all":
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
