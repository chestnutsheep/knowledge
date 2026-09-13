---
tags: [MOC, 行业]
title: "MOC-行业名称"
industry: "行业名称"
status: evergreen
updated: 2026-01-01
---

# MOC · {{industry}}

> 本页为「行业名称」的地图页（Map of Content），聚合该行业的**概念卡片、研报、看板、待办**，作为入口导航。

## 行业速览
- 定位：
- 景气位置：
- 关键变量：

## 概念卡片（产业链节点）
```dataview
LIST FROM "贰 • 杂学" WHERE contains(tags, "概念卡片") AND contains(file.tags, "{{industry}}")
SORT file.mtime DESC
```

## 关联研报（按发布日期倒序）
```dataview
TABLE org AS 机构, rating AS 评级, declareDate AS 发布日
FROM "肆 • 机构观点"
WHERE contains(industry, "{{industry}}")
SORT declareDate DESC
LIMIT 50
```

## 产业链可视化
- 见 Canvas：`[[产业链Canvas-行业名称]]`

## 看板与数据
- 

## Open Questions / 研究待办
- [ ] 

---

### 使用说明
- 每个一级行业建一张 `MOC-行业名.md`，放在 `肆 • 机构观点/` 或对应行业目录。
- Dataview 查询依赖研报笔记的 `industry` 字段与概念卡片的 `tags`，新建笔记务必套用对应标准件模板。
- 通过 `[[MOC-行业名]]` 从总览页与概念卡片双向跳转，构成"总览 → 概念 → 研报"三层检索网。
