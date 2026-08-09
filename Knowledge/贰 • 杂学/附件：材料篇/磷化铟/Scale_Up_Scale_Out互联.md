---
tags: [chip, interconnect, scaleup, scaleout]
up: ""
prev: ""
next: "[[光模块演化]]"
Raw-Material:
  - 铟
Functional-Material:
  - 磷化铟
Impact-Direction:
  - material: 铟
    cost_side: "光模块制造商"
    benefit_side: "铟矿资源商"
Data-Timestamp: "2026-06-26"
Confidence: "待验证"
---
# Scale‑Up / Scale‑Out：AI 互联的分水岭

## 1. 带宽需求

```chart
type: line
labels: [2024, 2025, 2026e, 2027e]
title: 单 XPU 互联带宽（Gbps）
series:
  - name: Scale‑Up
    data: [400, 800, 1600, 3200]
  - name: Scale‑Out
    data: [200, 400, 800, 1600]
```

## 2. 铜缆 vs 光互联

- 当前 Scale‑Up 端仍以铜缆为主，但铜缆在 1.6T 速率下 传输距离 < 1 米，无法满足机架间互联。
- 光互联渗透率：Scale‑Out 已 100% 光模块；Scale‑Up 光模块渗透率将从 2025 的 15% 提升至 2027 的 60%。

➡️ 光模块升级路径：[[光模块演化]]

---
反向链接