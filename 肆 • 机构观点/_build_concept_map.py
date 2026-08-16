#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逆检索：把研报按【概念/行业】归类，并匹配 notebook 已有主题板块。
输出 _concept_map.json 供构建 MOC 使用。"""
import os, re, json, glob
from pathlib import Path

REAL = Path("/home/AI/scapegoat_data/notebooks/知识库/肆 • 机构观点")
VAULT = Path("/home/AI/scapegoat_data/notebooks/知识库")

# 概念/行业词典：概念名 -> 关键词(在标题/正文中匹配)
CONCEPTS = {
    "人形机器人": ["人形机器人", "宇树", "智元", "机器人", "具身", "戴乐体感", "电子皮肤"],
    "半导体/先进封装": ["半导体", "PVD", "先进封装", "零部件", "射频电源", "UTG", "TGV", "光芯片", "有源芯片", "芯片", "信测通信", "检测龙头", "测试仪器仪表", "频准激光", "杰理科技", "平台化设备", "设备布局"],
    "AI算力/算电协同": ["AI", "算力", "液冷", "电通四海", "算启", "电源", "光通信", "光模块", "测试", "数据中心", "数据业务", "双中台", "AI+教育", "教辅", "AI存储", "封测"],
    "储能/新能源": ["储能", "组件", "锂", "海缆", "新能源", "绿电", "SAF", "固态", "风电"],
    "商业航天": ["商业航天", "航天", "卫星"],
    "脑机接口/脑科学": ["脑机", "脑科学"],
    "医药/CXO": ["CRDMO", "D&M", "ZG006", "泽布替尼", "创新药", "管线", "仿制药", "医佳宝", "灌流器", "生物资产", "实验室", "实体瘤", "CDM", "TIDES", "珈凯生物", "森合高科", "动保", "兽药", "金霉素"],
    "周期资源品": ["铜", "金", "锡", "镍", "银", "铟", "钴", "氨纶", "己二酸", "天然碱", "纯碱", "小苏打", "金属粉体", "MLCC", "电子树脂", "PTFE", "精细化学品", "钛", "周期品", "文莱炼厂", "矿山", "煤矿", "煤电", "动力煤", "巨龙铜业", "北交所"],
    "化工/材料": ["树脂", "涂料", "UV涂料", "高分子", "PTFE", "精细化学品", "苹果汁", "奶酪", "食品饮料", "化工"],
    "汽车/两轮车": ["比亚迪", "两轮车", "九号", "涛涛车业", "电动", "座椅", "汽车电子"],
    "消费/出海": ["出海", "东盟", "越南", "海外", "全球化", "东鹏", "饮料", "健盛", "百隆", "悍高", "五洲特纸", "炬申", "音飞", "文具", "消费", "渠道", "零售"],
    "物产/航运": ["运价", "集装箱", "航运", "油散", "物料处理", "物流"],
    "纸业/包装": ["浆纸", "特纸", "纸"],
    "金融/策略": ["策略", "A股", "资产配置", "宏观", "银行", "地产", "中小盘", "北交所", "新股"],
    "教育": ["教育", "教辅"],
    "量子": ["量子"],
    "银发经济": ["银发"],
    "个股中报业绩": [],  # 兜底类
}

def load_title(p):
    name = p.stem
    # 去 机构_日期_ 前缀
    m = re.match(r"^(.+?)_\d{4}-\d{2}-\d{2}_(.+)$", name)
    org, title = (m.group(1), m.group(2)) if m else ("?", name)
    return org, title, name

# notebook 已有可链接主题板块
EXISTING_TOPICS = {
    "产业链传递总览": "零 • 导览/产业链传递总览",
    "材料索引(贰杂学)": "贰 • 杂学/00-材料索引",
    "铟链(InP光芯片/高纯铟/上游铟矿)": None,  # 在产业链总览内
    "能源十五五规划": "叁 • 国家政策/新型能源体系建设“十五五”规划",
    "新型电力系统": "叁 • 国家政策/新型电力系统建设“十五五”规划",
    "地产策略": "叁 • 国家政策/地产2026下半年投资策略",
    "银行策略": "叁 • 国家政策/银行2026下半年投资策略",
    "包钢股份": "伍 • 基本信息池/包钢股份",
    "许继电气": "伍 • 基本信息池/许继电气",
    "中国卫星": "伍 • 基本信息池/中国卫星",
    "上海瀚讯": "伍 • 基本信息池/上海瀚讯",
    "音飞储存": "伍 • 基本信息池/音飞储存",
    "铜钴名单": "伍 • 基本信息池/铜钴核心上市公司名单",
}

results = {c: [] for c in CONCEPTS}
unmatched = []
for p in sorted(REAL.glob("*.md")):
    if p.name.startswith("00-") or p.name.startswith("README") or p.name.startswith("_"):
        continue
    org, title, stem = load_title(p)
    matched = []
    for c, kws in CONCEPTS.items():
        if any(k in title for k in kws):
            matched.append(c)
    if not matched:
        # 兜底：含"中报/半年报/业绩/Q2/H1/归母"等词的归入个股中报业绩
        if any(k in title for k in ["中报", "半年报", "业绩", "Q2", "H1", "归母", "营收", "净利润", "盈利", "分红", "超预期", "高增长", "拐点", "修复"]):
            matched = ["个股中报业绩"]
        else:
            unmatched.append(stem)
    else:
        for c in matched:
            results[c].append({"org": org, "title": title, "stem": stem, "link": f"[[{stem}]]"})

# 统计
print("=== 概念归类统计 ===")
for c, items in sorted(results.items(), key=lambda x: -len(x[1])):
    print(f"{c}: {len(items)} 篇")
print(f"\n未匹配: {len(unmatched)} 篇")
for u in unmatched:
    print("  -", u)

out = {"concepts": results, "unmatched": unmatched, "existing_topics": EXISTING_TOPICS}
(REAL / "_concept_map.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("\n已写出 _concept_map.json")
