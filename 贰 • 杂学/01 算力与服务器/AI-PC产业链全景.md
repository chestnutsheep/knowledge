---
tags:
  - AI算力
Raw-Material:
  - 硅
Functional-Material:
  - NPU
Impact-Direction:
  - material: 硅
    cost_side: 芯片制造环节
    benefit_side: 硅料/硅片供应商
Data-Timestamp: 2026-06-26
Confidence: 待验证
---

# AI PC 产业链全景图（2026）

> [!note] 来源说明
> 本文件整理自信息图《AI PC 产业链全景图(2026)：从 Copilot+ PC 到 AI Agent》。

## 什么是 AI PC？

**AI PC = CPU + GPU + NPU**，具备本地 AI 推理能力的新一代电脑。

| 特性 | 说明 |
|------|------|
| 本地运行大模型 | 无需云端，数据不出本地 |
| NPU 专属 AI 加速 | 40-50 TOPS+ 算力 |
| 数据安全 | 敏感数据本地处理 |

> [!quote] 核心判断
> AI 正在成为电脑的默认操作方式

## 上游：算力底座与硬件

### 1. 核心 AI 芯片

| 平台 | 产品 | AI 算力 | 定位 |
|------|------|---------|------|
| Intel | Core Ultra (Lunar Lake) | 40-50 TOPS+ | Copilot+ PC 主流 |
| AMD | Ryzen AI (Strix Point) | 40-50 TOPS+ | Copilot+ PC 主流 |
| Qualcomm | Snapdragon X Elite | 40-50 TOPS+ | Copilot+ PC 主流 |
| NVIDIA | DGX Spark | ~1000 AI TOPS (FP4) | 高性能路线 |

> [!important] NVIDIA DGX Spark
> - Grace CPU + Blackwell GPU
> - 128GB 统一内存
> - FP4 算力约 1000 AI TOPS
> - 面向开发者/研究者

### 2. 关键零部件升级

| 零部件 | 升级方向 | 说明 |
|--------|----------|------|
| 内存 | LPDDR5X / CAMM2 | 高带宽支持模型加载 |
| 存储 | PCIe 5.0 SSD | 高速读写模型权重 |
| 散热 | VC 均热板 | AI 负载持续高功耗 |
| 摄像头 | AI 摄像头 | 人眼追踪/高清 |
| 麦克风 | 阵列麦克风 | 智能降噪/远场拾音 |

## 中游：模型与软件生态

### 本地大模型（端侧运行）

| 模型 | 参数量 | 备注 |
|------|--------|------|
| Qwen | — | 阿里 |
| Llama | — | Meta |
| Phi | — | 微软 |
| MiniCPM | — | 面壁智能 |
| Gemma | — | Google |

- 主流 AI PC 支持 **7B-14B** 级模型流畅运行
- 高端平台（DGX Spark）支持 **70B** 级模型推理

### AI 软件生态

| 平台/框架 | 厂商 |
|-----------|------|
| Windows Copilot+ PC | 微软 |
| Apple Intelligence | 苹果 |
| OpenVINO | Intel |
| ONNX Runtime | 微软 |
| NVIDIA CUDA | 英伟达 |

## 下游：整机厂商

### 主要品牌

Lenovo 联想、DELL 戴尔、HP 惠普、ASUS 华硕、Acer 宏碁、苹果、HUAWEI 华为、HONOR 荣耀、小米、SAMSUNG 三星

### 核心竞争力

| 竞争力 | 说明 |
|--------|------|
| AI Agent 能力 | 个人专属智能体 |
| 生态整合能力 | 软硬协同，体验闭环 |
| 隐私与安全保障 | 本地运行，数据可控 |

## 应用落地场景

| 场景 | 说明 |
|------|------|
| AI 创作 | 文生图、视频生成 |
| AI 办公 | 智能助手、文档处理 |
| AI 开发 | 本地代码补全、调试 |
| AI 娱乐 | 游戏增强、内容推荐 |

## 趋势：从 Copilot+ PC 到 AI Agent

AI PC 演进路径：
1. **Copilot 阶段**：AI 作为辅助工具
2. **Agent 阶段**：AI 自主执行多步任务
3. **全域 Agent**：跨应用、跨场景自主决策

## 相关文件

- [[半导体结构总览]] — 芯片产业链导航地图
- [[半导体材料九大类]] — 硅片/电子特气等上游
- [[AIDC与算电协同]] — 算力基础设施
- [[人形机器人与具身智能]] — 机器人产业链

---
*信息来源：信息图《AI PC 产业链全景图(2026)》*
