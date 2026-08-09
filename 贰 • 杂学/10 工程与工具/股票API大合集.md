---
title: 股票行情 API 大合集
tags: [工程工具, 量化, 股票API, 数据源]
source: IMA 知识库（微信「小艾宝藏小铺」）
date: 2026-08-09
type: note
---

# 股票行情 API 大合集

> 来源：IMA 知识库微信文章（公众号「小艾宝藏小铺」）。核心观点：股票 API 是股市的「水电网」，决定了你获取行情信息的速度与稳定性。本文收集 4 个好用的行情 API。

## 四个推荐 API

1. **Alpha Vantage（Python 封装）** — 美股免费金融行情 API。
   链接：https://github.com/RomelTorres/alpha_vantage
2. **stocks.auto 行情工具** — 零运行时依赖，支持 Node.js、浏览器、CLI 和 MCP；自动从可用数据源获取行情；支持 A 股、港股、美股（GitHub 1.4K 星）。
   链接：https://github.com/zhangxianglian/stocks-auto
3. **雪球 API（pysnowball）** — 雪球行情 Python 库（GitHub 1.8K 星）。
   链接：https://github.com/unameyang/pysnowball
4. **TickDB 统一实时行情 API** — AI 原生实时行情数据 API，面向开发者、AI 代理和多市场金融应用；覆盖外汇、贵金属、指数、美股、港股、A 股、加密货币等的实时与历史行情。
   链接：https://github.com/TickDB/tickdb-unified-realtime-marketdata-api

## 选用建议

- 美股免费起步：Alpha Vantage。
- A/港/美全覆盖 + 想接 MCP/AI agent：stocks.auto（零依赖，最轻量）。
- 国内社区数据生态：雪球 pysnowball。
- 多市场实时+历史、对接 AI 应用：TickDB。

## 关联笔记

- 同目录见 [[贰 • 杂学/10 工程与工具/00-导航]]
- 量化数据源可与 [[拾 • 附件]] 行情研究交叉参考
