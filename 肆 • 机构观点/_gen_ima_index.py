#!/usr/bin/env python3
# 生成 IMA 收藏索引（按知识库分类 + 唯一性标记 + 可点击链接）。不伪造正文。
import json, os, re, subprocess, time

SKILL = "/home/scapegoat/.codebuddy/skills/ima-skills/ima_api.cjs"
ROOT = "/home/AI/scapegoat_data/notebooks/知识库"
KB = os.path.join(ROOT, "肆 • 机构观点", "_ima_kb_items.json")
CACHE = os.path.join(ROOT, "肆 • 机构观点", "_ima_urls.json")

d = json.load(open(KB, encoding="utf-8"))

# URL 缓存
url_cache = {}
if os.path.exists(CACHE):
    url_cache = json.load(open(CACHE, encoding="utf-8"))

def get_url(mid):
    if mid in url_cache:
        return url_cache[mid]
    if not mid.startswith("wechatarticle_"):
        url_cache[mid] = ""  # 图片类无 URL
        return ""
    try:
        r = subprocess.run(["node", SKILL, "openapi/wiki/v1/get_media_info",
                            json.dumps({"media_id": mid}, ensure_ascii=False)],
                           capture_output=True, text=True, timeout=30)
        j = json.loads(r.stdout.strip())
        u = j.get("data", {}).get("url_info", {}).get("url", "")
    except Exception:
        u = ""
    url_cache[mid] = u
    time.sleep(0.15)
    return u

# 现有笔记（重叠判断）
existing = []
for r, _, fs in os.walk(os.path.join(ROOT, "贰 • 杂学")):
    for f in fs:
        if f.endswith(".md"):
            existing.append(f[:-3])
def norm(s): return re.sub(r"[^\w一-鿿]", "", s)
ex = {norm(e): e for e in existing}
def overlap(title):
    tn = norm(title)
    for en, e in ex.items():
        if len(tn) >= 4 and len(en) >= 4 and (tn in en or en in tn):
            return e
    return None

BOARD_MAP = {
    "芯片": "07 半导体", "物理AI": "02 物理AI", "创新药": "03 创新药",
    "商业航天": "05 商业航天", "军工": "06 军工", "核电": "08 电力与储能",
    "政策方针": "十五五计划 / 00 宏观策略", "天灾": "（待建：天灾与周期）",
    "Coding": "10 工程与工具", "个股": "（待建：个股跟踪）",
}

articles = {}
for kb, v in d.items():
    fmap = {it["media_id"]: it["title"] for it in v["items"] if it.get("media_type") == 99}
    for it in v["items"]:
        if it.get("media_type") == 99:
            continue
        pid = it.get("parent_folder_id", "")
        folder = fmap.get(pid, "") if pid else ""
        mid = it.get("media_id", "")
        title = it.get("title", "")
        is_img = mid.startswith("img_")
        url = get_url(mid) if not is_img else ""
        hit = overlap(title)
        articles.setdefault(kb, []).append({
            "title": title, "media_id": mid, "folder": folder,
            "hit": hit, "url": url, "is_img": is_img,
        })

# 保存 URL 缓存（供后续提炼复用）
json.dump(url_cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

lines = ["---", "title: IMA 收藏索引（知识库）", "created: 2026-08-13", "type: ima-index", "---", "",
         "# IMA 收藏索引（知识库分类）", "",
         "> 来源：IMA 知识库（收藏的文章/图片，非笔记）。共 10 个分类库、151 条。",
         "> ⚠️ 正文抓取受限：微信文章 `get_media_info` 仅返回链接，且微信验证墙（环境异常）挡住命令行浏览器，暂无法提炼正文。本索引仅做导航 + 唯一性标记，**不伪造内容**。",
         "> 链接可直接点击跳微信原文（图片类标注 [图]）。待用户在 IMA 桌面端导出正文后，按「🆕新增」条目批量提炼进对应 notebook 板块。", ""]

total = new_ct = 0
for kb in ["芯片","物理AI","政策方针","创新药","天灾","核电","商业航天","军工","Coding","个股"]:
    items = articles.get(kb, [])
    if not items: continue
    lines.append(f"## {kb} （{len(items)} 条） → notebook 板块：{BOARD_MAP.get(kb,'')}")
    lines.append("")
    for a in items:
        total += 1
        if a["hit"]:
            tag = f"✅已覆盖≈{a['hit']}"
        else:
            tag = "🆕新增"; new_ct += 1
        loc = f"[{a['folder']}] " if a["folder"] else ""
        if a["is_img"]:
            title_md = f"{loc}**[图] {a['title']}**"
        elif a["url"]:
            title_md = f"{loc}[{a['title']}]({a['url']})"
        else:
            title_md = f"{loc}**{a['title']}**"
        lines.append(f"- {title_md}  `{tag}`")
    lines.append("")

lines += ["---", f"**统计**：条目 {total} ｜已覆盖 {total-new_ct} ｜新增 {new_ct}", "",
          "### 下一步",
          "- 新增中 notebooks 无专属板块者：`天灾`(建议建 天灾与周期)、`个股`(建议建 个股跟踪)；`核电`/`商业航天`/`军工` 已有弱板块可补强。",
          "- 正文来源方案确定后，优先补强：天灾、核电、商业航天、军工、个股。"]

out = os.path.join(ROOT, "肆 • 机构观点", "_IMA收藏索引.md")
open(out, "w", encoding="utf-8").write("\n".join(lines))
print(f"已生成。总{total} 新增{new_ct} 覆盖{total-new_ct}  URL缓存{len(url_cache)}")
