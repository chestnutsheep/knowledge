# 机构研报采集器 使用说明

## 功能
每个交易日 16:30 自动从**东方财富研报中心**拉取全市场最新券商研报，增量写入本目录（每篇独立成篇笔记），并刷新 `00-研报时间线.md`（按日期倒序、机构分组，展示「哪家机构 / 哪天 / 更新了什么观点」）。

## 数据源
- **主源：东方财富研报中心** `reportapi.eastmoney.com/report/list`
  - 全市场时间窗拉取（近 7 天），零 API Key、零依赖。
  - 返回：机构、发布日期、标题、东财评级、行业、标的、分析师、**原文 PDF 直链**。
  - 需代理 `127.0.0.1:7897`（与项目约定一致；代理关时东方财富不可达，会自动返回空，脚本不报错）。
- **补充源（可选）：金融界研报摘要** `JRJ_API_KEY` 配置后启用，提供摘要文本，与东方财富结果按文件名去重合并。

## 运行
```bash
cd "肆 • 机构观点"
python3 fetch_reports.py              # 正常采集（东方财富主源）
DRY_RUN=1 python3 fetch_reports.py    # 样例模式，无需网络/key
```

## 环境变量
- `DAYS_BACK`：回看天数，默认 7
- `JRJ_API_KEY`：可选，启用金融界补充摘要源
- `HTTPS_PROXY/HTTP_PROXY`：代理，默认 127.0.0.1:7897
- `VAULT_DIR`：Obsidian 库根目录（默认自动探测）

## 笔记结构
每篇研报落成 `机构_日期_标题前18字.md`，含 frontmatter（org / declareDate / source）与原文 PDF 链接、评级、行业、标的、分析师。timeline 页通过 Obsidian 双链 `[[笔记名]]` 跳转。

## 定时任务
「机构研报每日更新」recurring 任务：每周一至周五 16:30 执行 `python3 fetch_reports.py`，自动刷新 timeline 并回报本次新增篇数。
