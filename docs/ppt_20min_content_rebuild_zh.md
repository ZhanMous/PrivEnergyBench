# 20分钟面试汇报重构方案（基于最新项目进展）

## 目标
把当前18页内容重构为13页主讲+3页备用，突出三件事：
- 你做过什么（学术/项目经历）
- 你做成了什么（可证据化结果）
- 你下一步要做什么（类脑计算可执行展望）

## 总体节奏（20min）
- Part A 教育与定位：2分钟
- Part B 项目经历与结果：11分钟
- Part C 类脑计算基础与展望：6分钟
- Q&A 引导：1分钟

## 页级结构（13页主讲）

### 1. 封面（0:30）
- 标题建议：面向高能效与可信性的类脑计算研究实践
- 副标题建议：教育背景、项目经历与研究展望
- 只保留姓名+联系方式，不放长句承诺

### 2. 教育背景与研究定位（1:30）
- 1句背景：医学+计算机+法学的交叉输入
- 1句定位：用工程可复现的方法做类脑研究
- 1句能力：模型实现、评测基准、结果表达三位一体

### 3. 主线图：三项目如何形成闭环（1:00）
- MedSparseSNN：场景研究（医疗）
- Neuro-Symbiosis：机制探索（混合架构）
- PrivEnergyBench：评测基础设施（多目标）
- 结论：从“做模型”升级到“做可验证研究系统”

### 4. 项目一：MedSparseSNN 问题定义与方法（1:00）
- 问题：医疗任务中如何平衡精度、隐私、能效
- 方法：SNN / DenseSNN / ANN 对比 + MIA + 稀疏性分析
- 强调：采用可复现实验脚本与多次重复

### 5. 项目一：关键结果（1:30）
- 推荐图1（主图）：docs/clean_figures/med_accuracy_clean.png
- 推荐图2（辅图）：docs/clean_figures/med_mia_auc_clean.png
- 推荐图3（辅图）：docs/clean_figures/med_latency_energy_clean.png
- 口径：
  - PathMNIST准确率：SNN 82.33±0.31，ANN 85.12±0.40
  - 稀疏性收益：spike rate 0.1582，对应理论有效MAC节省约84.18%
  - MIA差异当前未显著，避免过度结论

### 6. 项目一：你学到什么（0:40）
- 结论1：SNN在能效维度有结构性优势
- 结论2：隐私差异需严格统计，不可凭单次结果下结论
- 结论3：GPU实测能耗不等于神经形态硬件收益，需分开表述

### 7. 项目二：Neuro-Symbiosis 方法与现状（1:10）
- 问题：SNN与Transformer混合能否实现效用-隐私-能效折中
- 现状：训练、隐私审计、能耗评估流程已打通
- 风险披露：当前数据以pipeline validation为主，LOSO级结论待真实受试者数据补齐

### 8. 项目二：关键图与当前证据（1:20）
- 推荐图1（主图）：docs/clean_figures/neuro_pareto_clean.png
- 推荐图2（辅图）：docs/redrawn_figures/neuro_coupling_threshold_energy_lines_redraw.png
- 可引用最新quick结果：
  - mia_auc≈0.466
  - attr_auc≈0.648
  - inversion_risk≈0.241
- 讲法：结果用于说明“评测链路可用”，不宣称最终科学结论

### 9. 项目三：PrivEnergyBench 的价值（1:20）
- 问题：不同模型、多指标、多seed怎么公平比较
- 能力：统一输出 accuracy/mia/attr/inversion/latency/energy + CI + dashboard
- 结论：把一次性实验沉淀为可复用评测底座

### 10. 项目三：基准结果（1:20）
- 推荐图1（主图）：outputs/default/pareto.png
- 推荐图2（辅图）：outputs/comparison_visuals/03_privacy_risk_radar_comparison.png
- 推荐图3（辅图）：outputs/comparison_visuals/01_metrics_comparison_table.png
- 讲法重点：
  - 不是“谁绝对最好”，而是“不同结构在目标间的可解释折中”
  - 强调多seed均值与CI，突出方法严谨性

### 11. 类脑计算基础（已有积累）（1:20）
- 你已经具备：
  - SNN训练与代理梯度
  - 稀疏性-能效分析（spike rate / effective MAC）
  - 隐私多攻击审计（MIA/属性推断/逆向风险）
- 这一页尽量不用愿景词，用“已完成能力清单”

### 12. 展望：未来12个月可执行计划（2:00）
- 方向A：真实受试者级BCI数据补齐，完成LOSO级科学结论
- 方向B：把隐私风险约束前移到训练目标（而非后验评测）
- 方向C：SNN在边缘端和联邦场景下的多目标联合优化
- 每个方向给出里程碑（3个月/6个月/12个月）

### 13. 总结与Q&A引导（0:30）
- 总结三句：
  - 我做了：模型+评测两条线并行推进
  - 我证明了：可以在真实约束下做可复现对比
  - 我下一步：补足数据条件，推进可发表结论
- Q&A提示：欢迎就统计显著性、复现路径、短板与改进追问

## 备用页建议（3页）
- A. 关键数值总表（含均值/标准差/CI）
- B. 复现路径（命令、数据入口、输出目录）
- C. 风险与边界（目前哪些结论成立，哪些还在验证）

## 当前18页到新结构的映射建议
- 保留并重写：1,2,3,4,5,6,7,9,12,15
- 合并：8+14 -> 新第11页（能力沉淀）
- 精简：10+11+13 -> 新第12页（12个月执行计划）
- 保留为备用：16,17,18

## 图表选用优先级（从高到低）
1) docs/clean_figures/med_accuracy_clean.png
2) docs/clean_figures/med_mia_auc_clean.png
3) docs/clean_figures/med_latency_energy_clean.png
4) docs/clean_figures/neuro_pareto_clean.png
5) outputs/default/pareto.png
6) outputs/comparison_visuals/03_privacy_risk_radar_comparison.png
7) outputs/comparison_visuals/01_metrics_comparison_table.png

## 讲述风格红线
- 不说“不可替代”“最快落地”等绝对化表达
- 不把quick实验当最终科学结论
- 不混用“GPU实测能耗优势”和“神经形态理论优势”

## 一句主线（建议反复出现）
我做的不只是模型精度优化，而是面向真实约束，把效用、隐私、能效放到同一套可复现框架里做研究。