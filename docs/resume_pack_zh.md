# PrivEnergyBench 简历文案包

## 一句话版本
PrivEnergyBench 是我独立实现的 PyTorch 模型三目标评测工具箱，可统一输出分类精度、成员推断风险与能耗代理指标，并自动生成多 seed 统计结果、Pareto 图和 HTML 展示页。

## 简历条目版本
**PrivEnergyBench | 隐私-能效-效用联合评测工具箱 | 独立开发**
- 面向 PyTorch 分类模型设计统一 benchmark 流程，集成训练、验证、成员推断攻击、时延测量与能耗代理估计。
- 支持 linear、MLP、CNN1D、Transformer 四类基线模型的多 seed 对比，自动输出 mean/std/95% CI、CSV 汇总、Markdown 报告和 HTML dashboard。
- 在默认 3-seed 实验中，MLP 达到最高验证精度 0.9208，Linear 保持最低能耗 0.0164 mJ/sample，形成清晰的 accuracy-energy trade-off 展示案例。

## 复试口述版
这个项目的核心不是提出一个新模型，而是把模型评测流程标准化。很多时候大家只看 accuracy，但实际系统里还要考虑隐私风险和推理成本。我做了一个轻量工具箱，把训练、成员推断攻击、延迟和能耗代理放在同一个基准里比较，并且支持多 seed 统计和自动出报告。这样后续不管是我的 MedSparseSNN，还是 Neuro-Symbiosis，都可以复用这套评测底座。

## 关键词
- PyTorch
- benchmark pipeline
- membership inference attack
- utility-privacy-energy trade-off
- multi-seed statistics
- HTML dashboard
- experiment automation

## 老师可能会追问的问题
1. 你为什么做这个工具，而不是再做一个模型？
回答：因为我希望解决“如何公平比较模型”的问题。研究里很多结论会被单次运行和单指标误导，所以我把多指标、多 seed 和自动报告整合进一个稳定流程。

2. 你的能耗为什么是 proxy，不是实测？
回答：当前版本为了轻量和可复现，用 latency × proxy power 的方式做统一比较。这个设计适合作为通用工具的第一版，后续可以替换成 GPU 实测功耗或硬件计数器。

3. 这个项目和你另外两个项目是什么关系？
回答：MedSparseSNN 和 Neuro-Symbiosis 更偏研究对象本身，PrivEnergyBench 更像评测基础设施。三者组合起来，能体现我既做模型，也做实验规范和工程工具。
