#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从研报正文提取 标的/行业/评级 精确字段，写回 frontmatter，并生成概念映射。"""
import re, json
from pathlib import Path

REAL = Path("/home/AI/Obsidian/知识库/肆 • 机构观点")

# 概念 -> 关键词（用于把行业/标的映射到上层概念卡片）
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

# industry 字段 -> 概念 的精确映射（优先用正文行业）
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
# 标题强信号（仅当 industry 为空或太泛时使用）
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

def infer_concept(metaObj):
    ind = (metaObj.get("industry") or "").strip()
    title = metaObj["stem"]
    if ind in INDUSTRY_MAP:
        return INDUSTRY_MAP[ind]
    # industry 太泛（设备/通用），用标题强信号
    for c, kws in TITLE_STRONG.items():
        if any(k in title for k in kws):
            return c
    return "个股中报业绩"

meta = {}
for p in REAL.glob("*.md"):
    if p.name.startswith(("00-", "README", "_")):
        continue
    txt = p.read_text(encoding="utf-8")
    # 优先从 frontmatter 读已有结构化字段（新格式已含）；缺失时再从正文 callout 抓
    fm = {}
    m = re.match(r"^---\n(.*?)\n---", txt, re.S)
    if m:
        for line in m.group(1).splitlines():
            kv = re.match(r'(\w+):\s*"?([^"\n]*)"?', line)
            if kv:
                fm[kv.group(1)] = kv.group(2).strip()
    obj = re.search(r"标的[：:]\s*([^\｜|]+)", txt)
    ind = re.search(r"行业[：:]\s*([^\｜|]+)", txt)
    rat = re.search(r"评级[：:]\s*([^\｜|]+)", txt)
    org = re.search(r"org:\s*\"?([^\"\n]+)\"?", txt)
    date = re.search(r"declareDate:\s*\"?([0-9-]+)\"?", txt)
    obj_v = fm.get("object") or (obj.group(1).strip() if obj else "")
    ind_v = fm.get("industry") or (ind.group(1).strip() if ind else "")
    rat_v = fm.get("rating") or (rat.group(1).strip() if rat else "")
    mobj = {"industry": ind_v, "object": obj_v, "stem": p.stem}
    concept = infer_concept(mobj)
    meta[p.stem] = {
        "object": obj_v, "industry": ind_v, "rating": rat_v,
        "concept": concept, "org": fm.get("org") or (org.group(1) if org else ""),
        "date": fm.get("declareDate") or (date.group(1) if date else ""),
    }
    # 原地更新 frontmatter：仅覆盖 concept/object/industry/rating（不重复插入）
    if not m:
        continue
    fm_block = m.group(1)
    new_block_lines = []
    seen = set()
    for line in fm_block.splitlines():
        kv = re.match(r'(\w+):', line)
        key = kv.group(1) if kv else None
        if key in ("concept", "object", "industry", "rating"):
            if key in seen:
                continue  # 去重：跳过后续重复行
            seen.add(key)
            val = {"concept": concept, "object": obj_v, "industry": ind_v, "rating": rat_v}[key]
            new_block_lines.append(f'{key}: "{val}"')
        else:
            new_block_lines.append(line)
    # 补齐缺失字段
    for key, val in (("concept", concept), ("object", obj_v), ("industry", ind_v), ("rating", rat_v)):
        if key not in seen:
            new_block_lines.append(f'{key}: "{val}"')
    new_txt = txt[:m.start(1)] + "\n".join(new_block_lines) + txt[m.end(1):]
    p.write_text(new_txt, encoding="utf-8")

# 统计概念分布
from collections import Counter
cnt = Counter(m["concept"] for m in meta.values())
print("=== 概念分布(写回frontmatter后) ===")
for c, n in cnt.most_common():
    print(f"{c}: {n}")
print(f"总计: {len(meta)} 篇")

json.dump(meta, open(REAL / "_meta.json", "w"), ensure_ascii=False, indent=2)
print("写出 _meta.json")
