---
dashboard: true
banner:
  quote: "The mind is everything. What you think you become."
  author: "Buddha"
  mode: stats
  statsConfig:
    streakFromDaily: false
    excludeFolders:
      - "叁 • 国家政策"
      - "壹 • 学术理论"
      - "TaskNotes"
      - "玖 • 模版"
      - "肆 • 机构观点/__pycache__"
      - "肆 • 机构观点/_pdf_cache"
    accent: "#bcf344"
    showDetails: true
    showLeft: true
    showCenter: true
    showRight: true
    leftStat: totalNotes
    centerStat: streak
    rightStats:
      - taskCompletion
      - connectivity
      - orphanRate
      - avgLinksPerNote
columns:
  - name: Memo
    color: "#f59e0b"
    type: memo
  - name: Todo
    color: "#6366f1"
    type: todo
  - name: Projects
    color: "#10b981"
    type: projects
  - name: Library
    color: "#8b5cf6"
    type: projects
  - name: 机构研报股票池
    color: "#10b981"
    type: dataview
    dataview:
      title: "近期机构研报覆盖（活清单）"
      query: "TABLE org AS 机构, rating AS 评级, concept AS 概念, declareDate AS 日期 FROM \"肆 • 机构观点\" WHERE contains(tags, \"研报\") SORT object ASC, declareDate DESC"
      excludeFolders:
        - "肆 • 机构观点/__pycache__"
        - "肆 • 机构观点/_pdf_cache"
  - name: 研报股票池·TOP
    color: "#0ea5e9"
    type: dataview
    dataview:
      title: "按覆盖篇数排名（股票 → 覆盖它的研报）"
      query: "TABLE length(rows) AS 覆盖篇数, rows.concept AS 概念, rows.rating AS 评级 FROM \"肆 • 机构观点\" WHERE contains(tags, \"研报\") GROUP BY object SORT length(rows) DESC LIMIT 40"
      excludeFolders:
        - "肆 • 机构观点/__pycache__"
        - "肆 • 机构观点/_pdf_cache"
---

## Memo

### 2026-08-26 备忘
id: demo-memo-1
欢迎使用 Apex Dashboard！点击此处编辑你的第一条备忘。

### 提示：Dashboard 文件路径
id: demo-memo-path
你可以在 设置 > Apex Dashboard 中修改 dashboard 文件路径。

### 提示：重命名分区
id: demo-memo-rename
双击分区标题即可重命名分区。

## Todo

### 快速上手
id: demo-todo-1
type: task
- [ ] 尝试添加一张新卡片
- [ ] 在不同分区之间拖拽卡片
- [ ] 编辑 Banner 区的名言
- [ ] 添加一个快捷链接

### 界面操作指南
id: demo-todo-2
type: task
- [ ] 点击左侧隐藏条拉出左侧栏
- [ ] 点击图钉按钮取消固定左侧栏
- [ ] 点击 Banner 区的书签按钮收起 Banner
- [ ] 在设置中开启更多小组件

## Projects

### 我的第一个项目
id: demo-project-1
type: project

## Library

### Reading
id: demo-lib-reading
type: project

### To Read
id: demo-lib-toread
type: project

### Done
id: demo-lib-done
type: project

## 机构研报股票池

## 研报股票池·TOP
