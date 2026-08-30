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
  DAYS_BACK         回看天数兜底上限 (默认 7；仅在笔记为空/无日期时回退使用)
  DRY_RUN           置 1 强制样例模式（无需网络/key）
  HTTP_PROXY/HTTPS_PROXY  代理（默认 127.0.0.1:7897，东方财富需代理）

采集窗口逻辑（增量自适应）：
  - 优先扫描已有研报笔记，取最大 declareDate = last_date 作为窗口起点 begin。
  - 终点 end = 今日。begin 当天**包含**在内，以兜底"上次扫描之后才更新"的研报，避免缺失。
  - 已有笔记按文件名去重跳过，不重复写入。
  - 仅当笔记为空或解析不到日期时，才回退到 now - DAYS_BACK 固定窗口。

用法：
  python3 fetch_reports.py            # 正常采集（东方财富主源，窗口=最后研报日期→今日）
  DRY_RUN=1 python3 fetch_reports.py  # 样例模式（无需网络/key）
"""

import os
import sys
import re
import json
import subprocess
import datetime as dt
from pathlib import Path

# ---------- 路径探测 ----------
# 候选 vault 列表（按优先级）：环境变量 > 实际在本机可用的路径。
VAULT_CANDIDATES = [
    "/home/AI/笔记/知识库",
    "/home/AI/Obsidian/知识库",
]

def _resolve_vault():
    env = os.environ.get("VAULT_DIR")
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    for c in VAULT_CANDIDATES:
        p = Path(c)
        if p.is_dir():
            return p
    # 都没有就退回第一个候选，让后续文件操作给出明确报错
    return Path(VAULT_CANDIDATES[0])

VAULT_DIR = _resolve_vault()
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


# ---------- 概念归类（单一真相；下游脚本统一从此词典推断） ----------
CONCEPT_KW = {
    "人形机器人": ["机器人", "宇树", "智元", "具身", "电子皮肤", "戴乐"],
    "半导体/先进封装": ["半导体", "PVD", "先进封装", "零部件", "射频电源", "UTG", "TGV", "光芯片", "芯片", "测试", "检测", "信测", "激光", "杰理", "设备"],
    "AI算力/算电协同": ["算力", "液冷", "数据中心", "AI", "光通信", "光模块", "电源", "数据业务", "存储", "封测"],
    "储能/新能源": ["储能", "组件", "锂", "海缆", "新能源", "绿电", "SAF", "固态", "风电", "光伏"],
    "商业航天": ["商业航天", "航天", "卫星"],
    "脑机接口/脑科学": ["脑机", "脑科学"],
    "医药/CXO": ["CRDMO", "CXO", "D&M", "创新药", "管线", "仿制药", "医佳宝", "灌流器", "生物", "实体瘤", "CDM", "TIDES", "医药", "制药", "生物制品", "兽药", "金霉素"],
    "周期资源品": ["铜", "金", "锡", "镍", "银", "铟", "钴", "氨纶", "己二酸", "碱", "纯碱", "小苏打", "金属粉体", "MLCC", "树脂", "PTFE", "精细化学品", "钛", "周期", "炼厂", "矿山", "煤矿", "煤电", "动力煤", "铝", "钢铁", "化工"],
    "化工/材料": ["树脂", "涂料", "高分子", "PTFE", "精细化学品", "化工", "材料", "塑料", "橡胶"],
    "汽车/两轮车": ["比亚迪", "两轮车", "九号", "涛涛", "电动", "座椅", "汽车", "车业"],
    "消费/出海": ["出海", "东盟", "越南", "海外", "全球化", "饮料", "食品", "健盛", "百隆", "悍高", "特纸", "炬申", "音飞", "文具", "零售", "消费", "奶酪", "果汁", "东鹏"],
    "物产/航运": ["运价", "集装箱", "航运", "油散", "物料", "物流"],
    "纸业/包装": ["浆纸", "特纸", "纸"],
    "金融/策略": ["策略", "A股", "资产", "宏观", "银行", "地产", "中小盘", "北交所", "新股", "证券", "金融"],
    "教育": ["教育", "教辅"],
    "量子": ["量子"],
    "银发经济": ["银发"],
}
INDUSTRY_MAP = {
    "半导体": "半导体/先进封装", "元件": "半导体/先进封装", "光学光电子": "半导体/先进封装",
    "通信设备": "半导体/先进封装", "计算机设备": "半导体/先进封装", "消费电子": "半导体/先进封装",
    "软件开发": "AI算力/算电协同", "IT服务": "AI算力/算电协同", "通信服务": "AI算力/算电协同",
    "电网设备": "储能/新能源", "电池": "储能/新能源", "光伏设备": "储能/新能源",
    "电力": "储能/新能源", "风电设备": "储能/新能源",
    "医疗器械": "医药/CXO", "医疗服务": "医药/CXO", "生物制品": "医药/CXO", "化学制药": "医药/CXO",
    "医药商业": "医药/CXO", "中药": "医药/CXO",
    "小金属": "周期资源品", "工业金属": "周期资源品", "贵金属": "周期资源品", "能源金属": "周期资源品",
    "煤炭": "周期资源品", "钢铁": "周期资源品", "金属新材料": "周期资源品", "化学原料": "周期资源品",
    "塑料": "化工/材料", "橡胶": "化工/材料", "化学制品": "化工/材料", "化学纤维": "化工/材料",
    "非金属材料": "化工/材料", "造纸": "纸业/包装", "包装印刷": "纸业/包装",
    "汽车零部件": "汽车/两轮车", "汽车整车": "汽车/两轮车", "摩托车及其他": "汽车/两轮车",
    "家居用品": "消费/出海", "服装家纺": "消费/出海", "饮料乳品": "消费/出海", "食品加工": "消费/出海",
    "厨卫电器": "消费/出海", "贸易": "消费/出海", "旅游零售": "消费/出海", "一般零售": "消费/出海",
    "航运港口": "物产/航运", "物流": "物产/航运",
    "证券": "金融/策略", "银行": "金融/策略", "保险": "金融/策略", "房地产": "金融/策略",
    "航天装备": "商业航天", "军工电子": "商业航天",
    "教育": "教育", "游戏": "AI算力/算电协同",
}
TITLE_STRONG = {
    "半导体/先进封装": ["半导体", "先进封装", "芯片", "PVD", "UTG", "TGV", "光模块", "光通信", "射频电源"],
    "人形机器人": ["人形机器人", "宇树", "智元", "具身", "电子皮肤"],
    "AI算力/算电协同": ["算力", "液冷", "AIDC", "数据中心", "算电"],
    "储能/新能源": ["储能", "固态", "海缆", "组件", "锂"],
    "商业航天": ["商业航天", "卫星"],
    "脑机接口/脑科学": ["脑机", "脑科学"],
    "医药/CXO": ["CRDMO", "CXO", "创新药", "管线", "仿制药"],
    "消费/出海": ["出海", "东盟", "越南", "全球化"],
}


def classify(industry: str, title: str) -> str:
    """统一概念归类：优先 industry 精确映射，否则标题强信号，最后兜底个股中报业绩。"""
    ind = (industry or "").strip()
    if ind in INDUSTRY_MAP:
        return INDUSTRY_MAP[ind]
    for c, kws in TITLE_STRONG.items():
        if any(k in (title or "") for k in kws):
            return c
    # 再走一遍宽泛关键词兜底
    for c, kws in CONCEPT_KW.items():
        if any(k in (title or "") for k in kws):
            return c
    return "个股中报业绩"


def note_id(declaredate: str, seq: int) -> str:
    """稳定的短文件名 ID：研报_YYYYMMDD_NNN.md（不塞标题）。"""
    d = (declaredate or "")[:10].replace("-", "")
    return f"研报_{d}_{seq:03d}"


def dedup_key(org: str, declaredate: str, title: str) -> str:
    """去重键：(日期, 机构, 标题) 归一，不依赖文件名。"""
    import unicodedata
    def norm(s):
        s = (s or "").strip().lower()
        s = unicodedata.normalize("NFKC", s)
        return re.sub(r"\s+", "", s)
    return "|".join([norm(org), norm(declaredate)[:10], norm(title)])


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


def fetch_via_eastmoney(begin: str, end: str = None) -> list:
    """调用东方财富研报中心接口，拉取 [begin, end] 时间窗内的全市场研报。

    接口: https://reportapi.eastmoney.com/report/list
    参数: code=* (全市场), beginTime/endTime 时间窗, pageSize 分页
    返回统一结构 list[dict]，字段含 pdfUrl。

    begin: 窗口起点 YYYY-MM-DD（含当天，用于兜底补漏）
    end:   窗口终点 YYYY-MM-DD（默认今日）
    """
    try:
        import requests
    except Exception as e:
        print(f"[ERROR] requests 不可用: {e}", file=sys.stderr)
        return []

    end_s = end or dt.datetime.now().strftime("%Y-%m-%d")
    begin_s = begin
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


def fetch_via_jrj(begin: str, end: str = None) -> list:
    """可选补充源：金融界研报摘要。需 JRJ_API_KEY。返回统一结构。"""
    if not os.environ.get("JRJ_API_KEY"):
        return []
    skill_dir = Path(os.environ.get("JRJ_SKILL_DIR",
                      "/home/scapegoat/.codebuddy/skills/jrj-fin-search-skill"))
    end_s = end or dt.datetime.now().strftime("%Y-%m-%d")
    start_s = begin + " 00:00:00"
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


def write_report_note(r: dict, seq: int = 1) -> str:
    """为单篇研报写独立笔记（frontmatter 承载全部结构化信息，文件名为短 ID）。
    已存在（按 (日期,机构,标题) 去重键）则跳过。返回笔记相对路径或 None。
    """
    import re as _re
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
    concept = classify(industry, title)

    # 去重：按 (日期,机构,标题) 归一键，扫描已存在笔记
    dk = dedup_key(org, date, title)
    for f in REPORTS_DIR.glob("*.md"):
        if f.name.startswith(("00-", "README", "_")):
            continue
        txt = f.read_text(encoding="utf-8", errors="ignore")
        om = _re.search(r'org:\s*"([^"]+)"', txt)
        dm = _re.search(r'declareDate:\s*"([^"]+)"', txt)
        tm = _re.search(r'title:\s*"([^"]*)"', txt)
        if om and dm and tm and dedup_key(om.group(1), dm.group(1), tm.group(1)) == dk:
            return None  # 已存在，增量跳过

    nid = note_id(r.get("declareDate", ""), seq)
    fpath = REPORTS_DIR / f"{nid}.md"
    # 防极端碰撞：同日同序号若已占，顺延
    while fpath.exists():
        seq += 1
        nid = note_id(r.get("declareDate", ""), seq)
        fpath = REPORTS_DIR / f"{nid}.md"

    object_field = f"{stock}({stock_code})" if stock else ""
    stock_line = f"｜ 标的：{object_field}" if stock else ""
    rating_line = f"｜ 评级：{rating}" if rating else ""
    indu_line = f"｜ 行业：{industry}" if industry else ""
    research_line = f"｜ 分析师：{researcher}" if researcher else ""
    pdf_line = f"\n> 原文 PDF：{pdf}" if pdf else "\n> 原文：详见东方财富研报中心（列表无直链）"

    # 概念维度标签：让 Dataview 能按概念聚合（如 tags 含 "概念/教育"）
    concept_tag = "概念/" + concept
    pdf_available = "true" if pdf else "false"

    # ---- 正文条件渲染：只有真实内容才写对应章节，避免 250 篇噪声明文 ----
    body = []
    # 来源 callout（含 frontmatter 已写的全部结构化信息，这里仅做人类可读摘要）
    body.append(f"> [!note] 来源")
    body.append(f"> {org}《{title}》")
    body.append(f"> 发布日期：{date} ｜ 数据来源：{src}{stock_line}{rating_line}{indu_line}{research_line}{pdf_line}")
    body.append("")
    # 核心观点：仅在有摘要时展开
    if abstract:
        body.append("## 核心观点")
        body.append("")
        body.append(abstract)
        body.append("")
    # 知识库交叉引用：由 _gen_obsidian.py 反向回填；此处先放占位锚，若已回填则保留
    body.append("## 知识库交叉引用")
    body.append("")
    body.append(f"- 概念归类：[[概念卡片/{concept.replace('/', '·')}]]")
    body.append("")
    # 风险因素：仅在有实质内容时展开（详情接口补抓后可用）
    if r.get("_risk"):
        body.append("## 风险因素")
        body.append("")
        body.append(r["_risk"])
        body.append("")
    body.append("---")
    body.append(f"*本文档由机构研报采集器自动生成（{dt.datetime.now().strftime('%Y-%m-%d %H:%M')}）｜源：{src}*")

    content = f"""---
tags: [机构观点, 研报, "{concept_tag}"]
org: "{org}"
declareDate: "{date}"
title: "{title}"
concept: "{concept}"
rating: "{rating}"
industry: "{industry}"
object: "{object_field}"
analyst: "{researcher}"
source: "{src}"
pdfUrl: "{pdf}"
pdfAvailable: {pdf_available}
---
# {title}

{chr(10).join(body)}
"""
    fpath.write_text(content, encoding="utf-8")
    return f"肆 • 机构观点/{nid}.md"


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
    """扫描目录下已有研报笔记，优先从 frontmatter 提取结构化字段（兼容新旧两种格式）。"""
    import re
    recs = []
    if not REPORTS_DIR.exists():
        return recs
    for f in REPORTS_DIR.glob("*.md"):
        if f.name.startswith(("00-", "README", "_")):
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        fm = {}
        m = re.match(r"^---\n(.*?)\n---", text, re.S)
        if m:
            for line in m.group(1).splitlines():
                kv = re.match(r'(\w+):\s*"?([^"\n]*)"?', line)
                if kv:
                    fm[kv.group(1)] = kv.group(2).strip()
        org = fm.get("org")
        date = fm.get("declareDate")
        title = fm.get("title")
        # 兜底：从 # 标题行取
        if not title:
            h = re.search(r'^#\s+(.+)$', text, re.M)
            title = h.group(1) if h else f.stem
            if org and date and title.endswith(f"（{org} {date}）"):
                title = title[: -(len(org) + len(date) + 4)]
        if not org:
            fn_m = re.search(r'（(.+?)(\d{4}-\d{2}-\d{2})）', f.stem)
            org = fn_m.group(1) if fn_m else "未知机构"
        if not date:
            fn_m = re.search(r'（(.+?)(\d{4}-\d{2}-\d{2})）', f.stem)
            date = fn_m.group(2) if fn_m else "0000"
        recs.append({
            "declareDate": (date + " 00:00:00") if len(date) == 10 else date,
            "orgName": org or "未知机构",
            "title": title or f.stem,
            "abstract": "",
            "rating": fm.get("rating", ""),
            "industry": fm.get("industry", ""),
            "stockName": (fm.get("object", "") or "").split("(")[0],
            "stem": f.stem,
            "note_rel": f"肆 • 机构观点/{f.name}",
        })
    return recs


def main():
    today = dt.datetime.now().strftime("%Y-%m-%d")

    # —— 自适应窗口：从已有笔记推算最后研报日期作为起点 ——
    existing_first = scan_existing_notes()
    last_date = ""
    for rec in existing_first:
        d = (rec.get("declareDate") or "")[:10]
        if d and (not last_date or d > last_date):
            last_date = d

    if last_date:
        begin = last_date  # 含当天：兜底"上次扫描之后才更新"的研报
        mode_desc = f"增量窗口 {begin} → {today}（从笔记最后研报日期起，含当天）"
    else:
        # 笔记为空/无日期：回退到固定回看天数
        begin = (dt.datetime.now() - dt.timedelta(days=DAYS_BACK)).strftime("%Y-%m-%d")
        mode_desc = f"回退窗口 {begin} → {today}（笔记为空，回看 {DAYS_BACK} 天）"

    print(f"[INFO] 模式: {'DRY_RUN(样例)' if DRY_RUN else '真实拉取(东方财富主源)'} | {mode_desc}")

    if DRY_RUN:
        items = SAMPLE_REPORTS
        print(f"[INFO] 样例研报 {len(items)} 篇")
    else:
        items = fetch_via_eastmoney(begin, today)
        print(f"[INFO] 东方财富返回研报 {len(items)} 篇")
        # 可选补充：金融界摘要（若配 key）
        if os.environ.get("JRJ_API_KEY"):
            jrj = fetch_via_jrj(begin, today)
            print(f"[INFO] 金融界补充 {len(jrj)} 篇")
            items = items + jrj

    # 写独立笔记（增量）；记录实际写入的短 ID（note_rel 形如 肆 • 机构观点/研报_YYYYMMDD_NNN.md）
    new_count = 0
    written_rels = set()
    for r in items:
        rel = write_report_note(r)
        if rel:
            new_count += 1
            written_rels.add(rel)
            print(f"[NEW] {rel}")
        else:
            print(f"[SKIP] 已存在: {r.get('orgName')} {r.get('title')}")

    # 合并历史记录 + 新写入记录，重建 timeline（复用已扫描的 existing_first）
    existing = existing_first
    seen = set()
    merged = []
    for rec in existing:
        key = rec.get("stem")
        if key in seen:
            continue
        seen.add(key)
        merged.append(rec)
    for rel in written_rels:
        f = REPORTS_DIR / Path(rel).name
        stem = f.stem
        txt = f.read_text(encoding="utf-8", errors="ignore")
        import re as _re
        def _g(pat):
            m = _re.search(pat, txt)
            return m.group(1) if m else ""
        merged.append({
            "declareDate": (_g(r'declareDate:\s*"([^"]+)"') + " 00:00:00") or "",
            "orgName": _g(r'org:\s*"([^"]+)"') or "未知机构",
            "title": _g(r'title:\s*"([^"]*)"'),
            "abstract": "",
            "rating": _g(r'rating:\s*"([^"]*)"'),
            "industry": _g(r'industry:\s*"([^"]*)"'),
            "stockName": (_g(r'object:\s*"([^"]*)"').split("(")[0]),
            "stem": stem,
            "note_rel": rel,
        })

    build_timeline(merged)
    print(f"[DONE] timeline 已更新: {TIMELINE_FILE} | 总收录 {len(merged)} 篇（本次新增 {new_count}）")


if __name__ == "__main__":
    main()
