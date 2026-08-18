---
tags: [SOP, 机构观点, 流程]
type: "SOP"
updated: 2026-08-13
---

# SOP：机构研报采集 → 概念卡片速览（Obsidian）构建流程

> 用途：每天（或定期）跑完研报采集后，把"肆 • 机构观点"下的研报按「研究对象/概念」逆检索归并，生成可在 Obsidian 里点击浏览的概念卡片体系。
> 适用：本知识库（notebooks/知识库）。脚本都在 `肆 • 机构观点/` 下，带 `_` 前缀，可重复运行、幂等。

## 一、前置条件
- 研报采集器 `fetch_reports.py` 已就绪（东方财富主源，回看 7 天）。
- 可选：~/.config/jrj/.env 配置 JRJ_API_KEY 以启用金融界补充源（未配则仅主源，不报错）。
- Obsidian 已装且启用的插件栈：dataview、obsidian-timeline、advanced-canvas、apex-dashboard、obsidian-charts、buttons、bases。
  - 说明：本环境为命令行，无法联网下载新插件；做"概念卡片速览"用现有栈足够。若要进一步美化可手动在 Obsidian 客户端装 banners / card-view，但非必需。

## 二、执行步骤（幂等，可重复跑）
1. 载入环境变量并跑采集（若 key 缺失走主源即可）：
   ```bash
   if [ -f ~/.config/jrj/.env ]; then set -a; . ~/.config/jrj/.env; set +a; fi
   cd "/home/AI/Obsidian/知识库/肆 • 机构观点" && python3 fetch_reports.py
   ```
   - 看到 `[INFO] 模式: 真实拉取` = 已拉真实数据；若 DRY_RUN = key 未配，仅重建 timeline，正常。
   - 错误码 42902=配额耗尽，40101=key 失效，需提示用户处理。

2. 提取正文「标的/行业/评级」并写回研报 frontmatter（concept/object/industry/rating 字段）：
   ```bash
   python3 _extract_meta.py
   ```
   - 概念推断优先级：**正文 industry 字段精确映射** > 标题强信号关键词 > 兜底「个股中报业绩」。
   - 分类字典在脚本顶部 `INDUSTRY_MAP` / `TITLE_STRONG`，随研报覆盖的行业扩充。

3. 生成 Obsidian 体系（MOC + 概念卡片 + Canvas + 逆检索索引）：
   ```bash
   python3 _gen_obsidian.py
   ```
   产出：
   - `00-研报概念速览.md` —— 主驾驶舱（Dashboard 仪表盘 + 概念卡片网格 + Timeline 入口 + 逆检索总索引 + Canvas 入口）。
   - `概念卡片/<概念名>.md` —— 每张卡 = 该概念全部研报清单（含标的/行业/评级）+ 逆检索到的 notebook 板块链接。
   - `研报概念架构.canvas` —— Advanced Canvas 可视化（研报→概念→notebook 板块）。
   - `研报逆检索索引.md` —— 从 notebook 板块视角反查相关研报概念。

4. 长文段去 AI 味：MOC/卡片的导读段用 Humanizer 风格撰写（已在 `_gen_obsidian.py` 文案中固化：去掉 emoji 装饰标题、去掉"设计逻辑/赋能/愿景"等腔，用口语化短句）。改文案只动 `_gen_obsidian.py` 里的字符串，重跑步骤 3 即可。

## 三、逆检索映射维护
- 概念 → notebook 板块的对应写在 `_gen_obsidian.py` 的 `CONCEPT_TO_BOARD` 字典。
- 新增研报概念或 notebook 新建了主题板块时，**只改这一个字典**，重跑步骤 3。
- 当前已挂接 17 个 notebook 板块（贰杂学的半导体/算力/储能/创新药/CXO/商业航天/材料索引、伍基本信息池的铜钴名单与个股、零导览的总览与产业链总览）。

## 四、常见坑
- 概念名含 `/`（如"半导体/先进封装"）不能做文件名 → 脚本用 `fname()` 转成 `·`。
- 研报笔记标题里可能含逗号/引号，链接用 `[[完整文件名]]` 最稳。
- 行业字段本身有噪声（如"计算机设备"被归到半导体），属可接受偏差；要更准就扩 `INDUSTRY_MAP`。
- `_` 开头的脚本与中间文件（_meta.json / _concept_map.json）是构建产物，可随时删除重跑。

## 五、待完善（持续迭代点）
- [ ] 研报正文若后续 API 提供 stockCode，可加 `stockCode` 字段做精确个股去重与个股 MOC。
- [ ] 人形机器人、消费出海等概念在 notebook 还没独立板块，可在贰杂学补建后挂接。
- [ ] 若装了 banners 插件，可给概念卡片加顶部 banner 图提升视觉。
- [ ] Dashboard 当前是占位代码块，需在 Obsidian 客户端确认 apex-dashboard 实际渲染（或改用 dataviewjs / charts 插件出图）。

---
*SOP 初版：2026-08-13，由自动化采集 + 概念速览构建任务沉淀。*

---

# 附录：IMA 收藏 → Obsidian 同步流程（2026-08-13 修正）

> ⚠️ **关键纠正**：用户收藏的是「文章」（分布在很多分类文件夹），对应 IMA 的 **knowledge-base（知识库）模块**，**不是 notes（笔记）模块**。第一轮误用 notes 模块（只列到 6 篇笔记且伪造增量）已回退。本文为修正版。

## 一、凭证
- clientId / apiKey 在 `~/.config/ima/client_id`、`~/.config/ima/api_key`。
- 调用：`node /home/scapegoat/.codebuddy/skills/ima-skills/ima_api.cjs <endpoint> <json-body> <opts-json>`。
- 注意：skill 有版本自检，报"需更新到 1.1.8"是误报（current 1.1.9 更高），**直接忽略重跑原请求即可**。

## 二、正确端点（knowledge-base）
1. 列全部知识库（=分类文件夹）：`openapi/wiki/v1/search_knowledge_base`，body `{"query":"","cursor":"","limit":20}`，返回 `data.info_list`，每项含 `kb_id`/`kb_name`/`item_num`（收藏数）。
2. 列某库内容（含子文件夹递归）：`openapi/wiki/v1/get_knowledge_list`，body `{"knowledge_base_id":<kb_id>,"cursor":"","limit":50,"folder_id":<可选>}`。
   - 返回字段是 `data.knowledge_list`（**不是** `info_list`）。
   - `media_type==99` 是文件夹，`folder_id` 传该项的 `media_id` 递归；`media_type==6` 是微信文章。
   - 翻页用 `data.next_cursor` + `data.is_end`。
3. 取文章：`get_media_info` 仅返回 `media_info.detail.url`（微信原文 URL），**不返回正文**。

## 三、步骤
1. 用 `_ima_kb_list.py` 拉全部知识库 + 所有收藏条目到 `_ima_kb_items.json`（已含递归 + 分类）。
2. **唯一性检验（关键）**：把收藏标题与 notebooks 现有笔记文件名做子串匹配（≥4字双向），标出「已覆盖」与「新增」。绝不给已覆盖主题重复建笔记。
3. 对新增主题，按知识库落到 notebooks 对应板块（`07 半导体`/`02 物理AI`/`03 创新药`/`05 商业航天`/`06 军工`/`08 电力与储能`/…），无专属板块的新建。
4. 正文提炼：见下方「正文抓取限制」。

## 四、正文抓取限制（已深挖验证，命令行无解）
- 微信文章 `get_media_info` 只给 URL；命令行 WebFetch/curl 拿不到正文（`js_content` 隐藏）。
- 已实测 **agent-browser 真实 Chromium**：`npm i -g agent-browser` + 经代理（`export HTTPS_PROXY=http://127.0.0.1:7897`）`agent-browser install` 下载 Chrome。打开微信 URL 仍触发「环境异常」验证墙，**非微信登录环境一律挡住，命令行无解**。
- 可行方案（按优先级）：
  1. 用户在 IMA 桌面端/微信打开文章，复制正文/导出，再交给我提炼（最可靠）；
  2. 用户提供微信有效 session Cookie 后带 Cookie 重试（仍不稳定）；
  3. **已落地索引方案**：`_gen_ima_index.py` 批量取微信 URL（图片类无 URL），生成 `_IMA收藏索引.md`（按 10 库分组、可点击跳原文、✅已覆盖/🆕新增 标记）。不伪造正文，避免"很乱"。
- **禁止**像第一轮那样凭空写「增量小节」——那是基于 notes 的误产物，已回退。

## 五、索引生成脚本（替代方案 3 的具体命令）
```bash
cd "肆 • 机构观点"
python3 _ima_kb_list.py      # 拉全部知识库+条目 → _ima_kb_items.json
python3 _gen_ima_index.py    # 批量取URL→_ima_urls.json，生成 _IMA收藏索引.md
```
`_ima_urls.json` 缓存 URL，后续用户给正文后可直接定位原文提炼；新增条目重新跑两步即可刷新索引。

## 五、本轮结果（2026-08-13）
- 真实收藏：10 个知识库、151 篇微信文章（芯片64/物理AI22/政策方针21/创新药18/天灾8/核电4/商业航天4/军工4/Coding4/个股2）。
- 唯一性：~20 篇与现有笔记重叠，~131 篇新增；最该补强的是 notebooks 尚无板块的 天灾/核电/商业航天/军工/个股。
- 因正文抓取受限，本轮仅完成盘点（`_IMA收藏盘点_2026-08-13.md`），未灌正文，待用户拍板正文来源后再按唯一性结论补强。
- 拉清单脚本：`_ima_kb_list.py`（替代已弃用的 `_sync_ima.py`）。
