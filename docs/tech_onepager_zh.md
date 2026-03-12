# PrivEnergyBench 一页技术说明

## 项目定位
PrivEnergyBench 是一个轻量级模型评测框架，面向 PyTorch 分类任务，统一衡量三类指标：
1. Utility：validation accuracy / loss
2. Privacy：confidence-based membership inference attack
3. Efficiency：latency / energy proxy

## 为什么需要它
实际项目中，模型选择不能只看精度。高精度模型可能推理成本更高，也可能更容易暴露训练成员信息。PrivEnergyBench 的目标是把这些维度放进统一实验流程，减少“只看单个指标”的片面判断。

## 核心功能
1. 通过 YAML 配置构建合成分类数据集并运行 benchmark。
2. 支持 linear、MLP、CNN1D、Transformer 四类模型基线。
3. 自动执行训练、验证、MIA、时延测量、能耗代理估计。
4. 支持多 seed 统计，输出 mean/std/95% CI。
5. 自动生成 CSV、Markdown 报告、Pareto 图和 HTML dashboard。

## 当前默认实验结果
基于 3 seeds 的默认配置：
- MLP：最高精度，val_acc_mean = 0.9208
- Linear：最低能耗，energy_mj_mean = 0.0164
- CNN1D：中等精度/中等隐私风险/较高能耗
- Transformer：参数较多、能耗较高，当前在合成任务上不占优

## 工程结构
- src/privenergybench/data.py：数据构建与 DataLoader
- src/privenergybench/models.py：模型工厂与基线实现
- src/privenergybench/train.py：训练与预测收集
- src/privenergybench/privacy.py：成员推断攻击评测
- src/privenergybench/energy.py：时延与能耗代理估计
- src/privenergybench/reporting.py：CSV/Markdown/HTML/Pareto 输出
- src/privenergybench/cli.py：统一入口

## 可扩展点
1. 替换合成数据为真实 tabular / vision / biosignal 数据集
2. 引入 shadow-model、loss-based 等更强 MIA
3. 接入真实 GPU power logging 而不是 proxy
4. 增加更多模型族和超参数 sweep

## 适合复试的价值点
1. 体现系统化实验设计能力，而非只会训练单个模型
2. 体现对隐私攻击、性能开销和统计可信度的综合理解
3. 具备独立项目闭环：配置、代码、测试、结果、展示材料齐全
