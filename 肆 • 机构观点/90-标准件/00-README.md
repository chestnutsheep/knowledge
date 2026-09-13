---
tags: [标准件, 索引]
title: "90-标准件 · 知识库标准模板索引"
status: evergreen
updated: 2026-09-13
---

# 90-标准件 · 标准模板索引

本目录存放知识库的**标准化组件模板**，所有新建笔记/看板应优先套用，以保证 frontmatter 字段统一、可被 Dataview 检索、可被反向链接聚合。

## 文件清单

| 文件 | 用途 | 适用对象 |
| --- | --- | --- |
| `研报笔记模板.md` | 单篇研报笔记的 frontmatter + 正文骨架 | 机构研报（自动采集后落库） |
| `行业概念卡片模板.md` | 行业/概念/产业链原子笔记的 frontmatter + 正文骨架 | 概念卡片、行业底稿 |
| `行业MOC模板.md` | 单个行业的 Map of Content（总览页） | 每个一级行业一张 |
| `产业链Canvas模板.md` | 产业链可视化 Canvas（JSON 骨架 + 说明） | 行业/主题可视化 |

## 统一约定（贯穿全部标准件）

1. **Frontmatter 必备字段**：`tags`、`title`、`status`、`updated`。
   - `status` 取生命周期值：`seedling → budding → evergreen → archived`。
   - `updated` 用 `YYYY-MM-DD`，重命名/修订时同步刷新。
2. **用户偏好的三字段**（研报类）已固化：
   - `org` = 机构（发布方）
   - `object` = 研究标的（代码/公司）
   - `declareDate` = 发布日期（`YYYY-MM-DD`）
3. **文件命名**：研报以**报告标题本身**命名；概念卡片以**概念/行业名**命名；MOC 以 `MOC-行业名` 命名。
4. **链接规范**：一律使用 `[[笔记名]]` 双向链接；跨目录引用写全路径 `[[目录/笔记名]]`；别名用 `[[笔记名|显示文本]]`。
5. **字段命名风格**：研报类用小驼峰（`declareDate`、`pdfUrl`）；行业概念类用带连字符的大写键（`Component`、`Raw-Material`、`Impact-Direction`），与采集器产出保持一致。

## 与采集器的关系

- `fetch_reports.py` 现已按"文件名 = 标题"落库；标题缺失时回退为 `研报_YYYYMMDD_NNN` 并保留原文件名（不强行改名，避免断链）。
- `_gen_obsidian.py` 重建索引时按 frontmatter 含 `研报` 判定研报笔记，与重命名后的标题文件兼容。
- 新增标准字段时，需同步更新这两个脚本的写入逻辑，否则增量采集会回退到旧 schema。
