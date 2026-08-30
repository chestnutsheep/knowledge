#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 Obsidian 概念卡片速览体系：
  - 00-研报概念速览.md  (主 MOC + Dashboard + Dataview)
  - 概念卡片/<概念>.md  (每张卡片页 = 列表 + 逆检索链接)
  - 研报概念架构.canvas (Advanced Canvas 可视化)
  - 研报逆检索索引.md   (反向挂到 notebook 各板块)
"""
import json, re, os
from pathlib import Path
from datetime import datetime

# ---------- 路径探测（与 fetch_reports.py 一致） ----------
VAULT_CANDIDATES = ["/home/AI/笔记/知识库", "/home/AI/Obsidian/知识库"]
def _resolve_vault():
    env = os.environ.get("VAULT_DIR")
    if env and Path(env).is_dir():
        return Path(env)
    for c in VAULT_CANDIDATES:
        if Path(c).is_dir():
            return Path(c)
    return Path(VAULT_CANDIDATES[0])
VAULT = _resolve_vault()
REAL = VAULT / "肆 • 机构观点"

# ---------- 直接从当前研报笔记 frontmatter 重建元数据（不依赖陈旧的 _meta.json） ----------
def _scan_meta():
    meta = {}
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
        meta[p.stem] = {
            "concept": d.get("concept", "个股中报业绩"),
            "date": d.get("declareDate", ""),
            "org": d.get("org", ""),
            "object": d.get("object", ""),
            "industry": d.get("industry", ""),
            "rating": d.get("rating", ""),
        }
    return meta
meta = _scan_meta()

# 概念 -> notebook 已有逆检索板块 (逆检索核心)
CONCEPT_TO_BOARD = {
    "半导体/先进封装": [
        "贰 • 杂学/07 半导体/先进封装/先进封装与Chiplet",
        "贰 • 杂学/07 半导体/半导体设备/半导体设备产业链全景",
        "贰 • 杂学/07 半导体/光通信/光模块产业链全景",
        "贰 • 杂学/07 半导体/半导体材料/封装与载板/TGV玻璃基板",
    ],
    "AI算力/算电协同": [
        "贰 • 杂学/01 算力与服务器/超节点产业链",
        "贰 • 杂学/08 电力与储能/AIDC与算电协同",
        "贰 • 杂学/09 科技投资研究/算电协同",
    ],
    "储能/新能源": [
        "贰 • 杂学/08 电力与储能/储能：固态电池/固态电池产业链全景",
        "贰 • 杂学/08 电力与储能/储能：固态电池/储能PCS四大演进",
    ],
    "医药/CXO": [
        "贰 • 杂学/03 创新药/CXO与创新药产业链",
    ],
    "人形机器人": [
        "贰 • 杂学/02 物理AI/人形机器人/人形机器人整机",
        "贰 • 杂学/02 物理AI/人形机器人/人形机器人与具身智能",
    ],
    "商业航天": [
        "贰 • 杂学/05 商业航天/商业航天产业链全景",
        "零 • 导览/产业链传递总览",
    ],
    "周期资源品": [
        "伍 • 基本信息池/铜钴核心上市公司名单",
        "零 • 导览/产业链传递总览",
    ],
    "汽车/两轮车": [
        "贰 • 杂学/11 汽车与两轮车/汽车与两轮车",
    ],
    "物产/航运": [
        "贰 • 杂学/12 航运物流/航运物流",
    ],
    "消费/出海": [
        "贰 • 杂学/附件：材料篇/稀土篇/稀土永磁出海分析",
        "伍 • 基本信息池/东鹏饮料" if (VAULT/'伍 • 基本信息池/东鹏饮料.md').exists() else "伍 • 基本信息池",
    ],
    "纸业/包装": ["贰 • 杂学/14 纸业与包装/纸业与包装"],
    "金融/策略": ["叁 • 国家政策/银行2026下半年投资策略", "叁 • 国家政策/地产2026下半年投资策略"],
    "化工/材料": ["贰 • 杂学/00-材料索引"],
    "教育": ["贰 • 杂学/13 教育/教育"],
    "量子": ["贰 • 杂学/09 科技投资研究/未来5年科技投资全景"],
    "银发经济": ["贰 • 杂学/09 科技投资研究/未来5年科技投资全景"],
    "个股中报业绩": ["零 • 导览/知识库总览"],
}

# 概念配色（用于 Canvas / Dashboard）
CONCEPT_COLOR = {
    "半导体/先进封装": "#7c5cff",
    "AI算力/算电协同": "#2d9cdb",
    "储能/新能源": "#27ae60",
    "医药/CXO": "#e84393",
    "人形机器人": "#e67e22",
    "周期资源品": "#b9770e",
    "消费/出海": "#16a085",
    "汽车/两轮车": "#c0392b",
    "商业航天": "#8e44ad",
    "物产/航运": "#2980b9",
    "纸业/包装": "#a04000",
    "金融/策略": "#34495e",
    "化工/材料": "#7f8c8d",
    "教育": "#d35400",
    "量子": "#0abde3",
    "银发经济": "#e84393",
    "个股中报业绩": "#95a5a6",
}

# 按概念聚合
from collections import defaultdict
by_concept = defaultdict(list)
for stem, m in meta.items():
    by_concept[m["concept"]].append(stem)

# ---------- 反向回填：把"概念卡片 + 逆检索板块"写回每篇研报笔记 ----------
def fname(concept):
    return concept.replace("/", "·")

def backfill_crossref():
    """让孤岛变网状：为每篇研报笔记的「## 知识库交叉引用」章节，
    填入它归属的概念卡片 + 逆检索到的 notebook 板块链接。
    仅重写该章节（从章节标题到文末分隔线之前），不动来源 callout / 核心观点。
    """
    crossref_pat = re.compile(
        r"## 知识库交叉引用.*?(?=\n---|\Z)", re.S
    )
    updated = 0
    for stem, m in meta.items():
        concept = m.get("concept", "个股中报业绩")
        boards = CONCEPT_TO_BOARD.get(concept, [])
        card_link = f"[[概念卡片/{fname(concept)}]]"
        lines = ["## 知识库交叉引用", ""]
        lines.append(f"- 概念归类：{card_link}")
        if boards:
            lines.append("- 逆检索到的知识库板块：")
            for b in boards:
                lines.append(f"  - [[{b}]]")
        else:
            lines.append("- 逆检索板块：（暂无对应 notebook 板块，可在贰杂学/伍基本信息池新建主题笔记）")
        block = "\n".join(lines) + "\n"

        fpath = REAL / f"{stem}.md"
        if not fpath.exists():
            continue
        text = fpath.read_text(encoding="utf-8")
        # 只替换「## 知识库交叉引用 ... 到 --- 之前」这一段
        new_text, n = crossref_pat.subn(lambda mm: block.rstrip("\n"), text)
        if n:
            fpath.write_text(new_text, encoding="utf-8")
            updated += 1
    return updated

_xref = backfill_crossref()
print(f"[INFO] 反向回填知识库交叉引用：{_xref} 篇研报笔记已写入概念卡片+逆检索板块链接")

# 概念卡片页
card_dir = REAL / "概念卡片"
card_dir.mkdir(exist_ok=True)
def fname(concept):
    return concept.replace("/", "·")
for concept, keylist in by_concept.items():
    items = [meta[k] for k in keylist]
    items.sort(key=lambda x: x["date"], reverse=True)
    boards = CONCEPT_TO_BOARD.get(concept, [])
    board_links = "\n".join(f"- [[{b}]]" for b in boards) or "- （暂无对应 notebook 板块，可在贰杂学/伍基本信息池新建主题笔记）"
    lines = [
        f"---",
        f'tags: [机构观点, 概念卡片, "{concept}"]',
        f'concept: "{concept}"',
        f'count: {len(items)}',
        f"---",
        f"# {concept} · 概念卡片",
        f"",
        f"> 「肆 • 机构观点」里研究对象属于 **{concept}** 的研报，一共 {len(items)} 篇，都收在这张卡里。",
        f"> 点条目进具体研报；卡片底部的「逆检索到的知识库板块」能跳到你之前写过的主题研究。",
        f"",
        f"## 本概念研报清单（按日期倒序）",
        f"",
        f"| 日期 | 机构 | 研报 | 标的 | 行业 | 评级 |",
        f"|------|------|------|------|------|------|",
    ]
    for k in keylist:
        it = meta[k]
        lines.append(f"| {it['date']} | {it['org']} | [[{k}]] | {it['object'] or '—'} | {it['industry'] or '—'} | {it['rating'] or '—'} |")
    lines += [
        f"",
        f"## 逆检索到的知识库板块",
        f"",
        board_links,
        f"",
        f"---",
        f"*这张卡是研报概念速览生成器自动出的（{datetime.now():%Y-%m-%d}）。回主驾驶舱：[[00-研报概念速览]]*",
        f"",
    ]
    card_path = card_dir / f"{fname(concept)}.md"
    if card_path.exists():
        ext = card_path.read_text(encoding="utf-8")
        mcons = re.search(r"## 共识综述.*?(?=\n---|\Z)", ext, re.S)
        if mcons:
            for i, l in enumerate(lines):
                if l == "---" and i + 1 < len(lines) and lines[i + 1].startswith("*这张卡"):
                    lines[i:i] = [mcons.group(0).rstrip(), ""]
                    break
    card_path.write_text("\n".join(lines), encoding="utf-8")

# 主 MOC 页面（Dashboard + Dataview + 卡片网格）
concept_sorted = sorted(by_concept.items(), key=lambda x: -len(x[1]))
total = len(meta)
moc = []
moc += [
    "---",
    "tags: [机构观点, 导航, dashboard]",
    'type: "研报概念速览"',
    f"total: {total}",
    "updated: " + datetime.now().strftime("%Y-%m-%d"),
    "---",
    "# 研报概念速览",
    "",
    f"> 截至 2026-08-12，机构观点库里攒了 {total} 篇研报。光按时间翻太累，所以按「研究对象属于哪个概念」重新切了一刀，归成 {len(concept_sorted)} 张卡片。",
    "> 点卡片进去看具体研报；每张卡片底部挂着 notebook 里已有的相关板块，顺着链接就能从机构观点摸到自己的研究底稿。",
    "",
    "## 一、概念分布仪表盘（Apex Dashboard）",
    "",
    "```dashboard",
    "title: \"各概念研报数量分布\"",
    "type: bar",
    "```",
    "",
    "> 上方为静态预览；下方 Dataview 为**活清单**，新增研报笔记后自动聚合，无需重跑脚本。",
    "",
    "```dataview",
    "TABLE org AS 机构, object AS 标的, rating AS 评级, industry AS 行业",
    "FROM \"肆 • 机构观点\"",
    "WHERE type != \"研报概念速览\" AND contains(tags, \"研报\")",
    "SORT concept ASC, declareDate DESC",
    "```",
    "",
    "## 二、概念卡片网格",
    "",
    "> 每张卡片是一个概念入口，里面是该概念下的全部研报，外加逆检索出来的 notebook 板块。",
    "",
]
# 卡片表格
moc.append("| 概念 | 篇数 | 入口 |")
moc.append("|------|------|------|")
for concept, items in concept_sorted:
    color = CONCEPT_COLOR.get(concept, "#888")
    moc.append(f"| <span style='color:{color};font-weight:600'>{concept}</span> | {len(items)} | [[概念卡片/{fname(concept)}\\|进入]] |")
moc += [
    "",
    "## 三、研报时间线（Timeline 插件）",
    "",
    "> 按日期倒序的原始研报流，详见 [[00-研报时间线]]。",
    "",
    "## 四、逆检索总索引",
    "",
    "下面这些 notebook 板块已经和研报概念串起来了：",
    "",
]
# 逆检索板块汇总
all_boards = []
for concept, items in concept_sorted:
    for b in CONCEPT_TO_BOARD.get(concept, []):
        if b not in all_boards:
            all_boards.append(b)
for b in all_boards:
    moc.append(f"- [[{b}]]")
moc += [
    "",
    "## 五、概念架构图（Advanced Canvas）",
    "",
    "> 研报怎么归到概念、概念又连到哪些 notebook 板块，一张图看全，见 [[研报概念架构]]。",
    "",
    "---",
    f"*这页是研报概念速览生成器自动出的（{datetime.now():%Y-%m-%d %H:%M}），数据源是东方财富研报中心。*",
    "",
]
(REAL / "00-研报概念速览.md").write_text("\n".join(moc), encoding="utf-8")

# Canvas 架构图
def canvas_node(id, x, y, text, color, kind="text"):
    return {
        "id": id, "type": "text" if kind == "text" else "file",
        "text": text, "x": x, "y": y, "width": 240, "height": 90,
        "color": color,
    }

nodes = []
edges = []
# 中心
nodes.append(canvas_node("root", 520, 360, "# 📊 研报概念速览\n162篇研报 · 17概念", "#1f2937", "text"))
x0, y0 = 100, 80
col = 0
for i, (concept, items) in enumerate(concept_sorted):
    cx = 60 + (i % 4) * 300
    cy = 60 + (i // 4) * 160
    cid = f"c{i}"
    color = CONCEPT_COLOR.get(concept, "#888")
    nodes.append(canvas_node(cid, cx, cy, f"🧩 {concept}\n{len(items)}篇\n[[概念卡片/{fname(concept)}]]", color))
    edges.append({"id": f"e_root_{cid}", "fromNode": "root", "fromSide": "top", "toNode": cid, "toSide": "bottom"})
# notebook 板块节点
boards_unique = all_boards
for j, b in enumerate(boards_unique):
    bid = f"b{j}"
    nodes.append(canvas_node(bid, 1100 + (j % 3) * 300, 60 + (j // 3) * 130,
                              f"📁 {b.split('/')[-1]}\n[[{b}]]", "#0e7490"))
canvas = {
    "nodes": nodes,
    "edges": edges,
    "version": 1.1,
    "direction": "right",
}
(REAL / "研报概念架构.canvas").write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")

# 逆检索交叉索引页（反向挂到 notebook）
inv = [
    "---",
    "tags: [机构观点, 导航, 逆检索]",
    "---",
    "# 研报逆检索索引",
    "",
    "> 这一页换个方向看：不从研报出发，而从 notebook 已有的主题板块出发，回看哪些机构观点跟它相关。",
    "",
]
for b in all_boards:
    inv.append(f"## [[{b}]]")
    rel = [c for c, items in concept_sorted for _ in [0] if b in CONCEPT_TO_BOARD.get(c, [])]
    inv.append("")
    inv.append("相关研报概念：" + "、".join(f"[[概念卡片/{c}]]" for c in rel))
    inv.append("")
(REAL / "研报逆检索索引.md").write_text("\n".join(inv), encoding="utf-8")

print(f"生成完成：主MOC + {len(concept_sorted)} 张概念卡片 + Canvas + 逆检索索引")
print(f"逆检索板块数：{len(all_boards)}")
