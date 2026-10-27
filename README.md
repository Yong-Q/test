# OFF → POLAR 轨迹重加权与直接关联函数

本项目研究能否利用计算成本较低的参考势生成轨迹，再用目标势逐帧重新计算能量，通过重要性重加权估计目标体系的平衡统计量。当前以 **MACE-OFF → MACE-POLAR** 为实例，目标是获得可用于经典密度泛函研究的密度、关联结构以及 c₁/c₂。

代码提供轨迹生成、能量重评估、权重与 ESS 诊断，以及实验性的 RDF、OZ 反演和 Widom 工具。重加权接口也接受其他 ASE 计算器，应用到 UFF 或其他参考势时需要重新验证采样分布与目标势的重叠。

**当前进展：** 权重和 ESS 已独立复算；RDF 球壳体积错误已修复并增加测试。Widom 平均、OZ 径向网格、温度约定和统计审核仍有待完成项，因此随仓 c₁/c₂ 暂不作为已认证的训练标签。详细证据见[检查记录](docs/AUDIT_2026-10-23.md)，具体修改与验收步骤见[实施计划](docs/superpowers/plans/2026-10-23-polar-c1c2-validation.md)。

**2026-10-27更新：** 501帧ESS独立复算为2.34867；另修复独立500ps脚本的RDF配对归一化，并发现源轨迹z向明显不均匀。论文中的逐帧Δ能量校正、重叠不足时重新采样，以及后续验收事项，统一列于[最新TODO](docs/TODO_OFF_POLAR_2026-10-27.md)；[复算数据与诊断图](docs/results/20261027_off_polar_audit/)单独保存，旧结果不覆盖。

**学生→POLAR（2026-10-27）：** 1,152 原子一步重加权 σ_β=8.02、ESS 0.24 %（最大单帧权重 91.5 %）；96 原子 ESS≈44 %，气相 98 %。生产尺寸判为不可用，详见[ESS 报告](docs/ESS_STUDENT_TO_POLAR_2026-10-27.md)。

## 文献中的逐帧校正与重加权（为什么他们能工作）

| 工作 | 做法 | 关键条件 | 与本项目（OFF→POLAR / 学生→POLAR）的差别 |
|---|---|---|---|
| Herzog et al., JCTC 18, 1382 (2022) | MLPT：学习构型相关 ΔU 再配权；MLMC：用校正势 U_corr=U_L+f(R) **重新采样**，再对残差配权 | 约 19,000 构型中选 200 训练 + 25 测试；目标是吸附焓；ΔU 是同一体系两个电子结构层级之间的小修正 | 我们跨两个不同势（长程静电不同），c₁/c₂ 是整盒结构量，不是局部吸附能 |
| Chehaibou et al., JCTC 15, 6333 (2019) | 用 MLPT 计算 RPA 吸附焓 | 同类小扰动 + 局部观测量 | 同上 |
| Hilpert & Kresse, JCP 164, 194504 (2026) | 63 个水分子、292 K，5,000 个去相关构型，逐帧 DFT−MLIP ΔU，对体积配权 | MACE 的 ESS≈4,200、KbP<800；目标与 MLIP 都是同一个 RPBE-D3 DFT | 同目标势；我们不是同目标，且 1,152 原子使 ΔU 方差随 N 增长 |
| Thaler & Zavadlav, Nat Commun (2021) | 可微轨迹重加权，从实验数据学势 | 重加权嵌入训练循环，误差可反向传播 | 我们是固定模型的事后诊断 |
| Shirts & Chodera, JCP 129, 124105 (2008) | MBAR：多个平衡态联合估计 | 需要多个中间态/λ 的**真实采样**，相邻态重叠高 | 我们只有单源单目标；需按 [Task 6](docs/superpowers/plans/2026-10-23-polar-c1c2-validation.md) 补 λ 中间势 |

共同点：(i) 扰动小或同目标（同一 DFT 泛函的 MLIP），不是两个不同势；(ii) 用中间态/BAR/MBAR 或校正势**重新采样**，而不是一步跳；(iii) 体系小或样本大（数千去相关构型、ESS 数千）；(iv) 观测量是局部量/自由能，不是整盒 c₁/c₂。我们的 1,152 原子一步重加权 ESS 只有 0.24–0.47 %，正是不满足这些条件的后果；详见[ESS 报告](docs/ESS_STUDENT_TO_POLAR_2026-10-27.md)。

引用：

1. Herzog et al. *Assessing the Accuracy of Machine Learning Thermodynamic Perturbation Theory: Density Functional Theory and Beyond.* JCTC 18, 1382–1394 (2022). [DOI](https://doi.org/10.1021/acs.jctc.1c01034) · [arXiv 全文](https://arxiv.org/html/2110.06818)
2. Chehaibou et al. *Computing RPA Adsorption Enthalpies by Machine Learning Thermodynamic Perturbation Theory.* JCTC 15, 6333–6342 (2019). [DOI](https://doi.org/10.1021/acs.jctc.9b00782)
3. Hilpert & Kresse. *Accurate thermophysical properties of water using machine-learned potentials.* JCP 164, 194504 (2026). [DOI](https://doi.org/10.1063/5.0325444) · [arXiv 全文](https://arxiv.org/html/2601.21103v1)
4. Thaler & Zavadlav. *Learning neural network potentials from experimental data via Differentiable Trajectory Reweighting.* Nat Commun (2021). [论文](https://www.nature.com/articles/s41467-021-27241-4)
5. Shirts & Chodera. *Statistically optimal analysis of samples from multiple equilibrium states.* JCP 129, 124105 (2008). [DOI](https://doi.org/10.1063/1.2978177) · [开放全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC2671659/)

## 方法

对于相同温度、粒子数、体积和约束下的源体系与目标体系，在第 $i$ 帧完整构型 $X_i$ 上计算总势能差：

$$
\Delta U_i=U_{\mathrm{target}}(X_i)-U_{\mathrm{source}}(X_i),
\qquad
\widetilde w_i=
\frac{\exp(-\beta\Delta U_i)}{\sum_j\exp(-\beta\Delta U_j)},
\qquad \beta=(k_BT)^{-1}.
$$

目标平衡平均由加权统计估计：

$$\langle A\rangle_{\mathrm{target}}\approx\sum_i\widetilde w_i A(X_i),\qquad N_{\mathrm{eff},w}=\frac{1}{\sum_i\widetilde w_i^2}.$$

能量差使用**整帧总能量**。若两体系的外场不同，还需包含外场总能量差；相同外场会抵消。计算指数前减去最大的对数权重可避免溢出，固定粒子数下的全局能量常数也会在归一化时抵消。

ESS 衡量权重集中程度，本身不处理轨迹自相关，也不保证某个观测量准确。判断 c₁/c₂ 是否可用，还需要平衡与分块检查、有限尺寸分析，以及独立目标势的参照。当前程序返回的 `usable`、`marginal`、`collapse` 是启发式诊断标记，不能直接作为训练标签的合格判定。

## c₁/c₂ 的范围

| 量 | 提取方式与当前边界 |
|---|---|
| 密度、RDF、结构因子等平衡统计 | 对构型对应的统计量加权；不能用重加权恢复目标势的真实时间演化 |
| 均相 c₂ | 先加权关联统计，再用适用的 OZ/响应关系提取；当前代码是 O–O RDF 的标量 OZ 路径，不能当作完整位置—取向分子 c₂ |
| 均相绝对 c₁ | 需要目标化学势和一致的分子理想参考；已有 Widom 工具仍需修复与验收 |
| 外场下中心化 c₁ | 可由目标密度和目标外场的 EL 关系提取，化学势常数可消除；完整标签流程尚待集成验收 |

c₁、c₂(r) 为无量纲量，傅里叶 c₂(k) 的单位为 Å³。用于 BZA 分子模型时需统一 COM 密度、原子位点密度和取向投影的定义。能量拟合中的 `linear.slope`、`linear.intercept_eV` 与这里的直接关联函数 c₁/c₂ 无关。

## 安装与检查

使用 Python 3.10 或更高版本。从仓库根目录安装基本依赖和测试工具；当前 Widom/审计路径还需要 SciPy：

```bash
python -m pip install -e ".[test]" scipy
python -m pytest tests -q
```

不加载 MACE 模型，也能重放随仓数据的 CPU 检查。输出文件必须使用一个尚不存在的路径：

```bash
python validation/audit_existing_results.py --output runs/audit-check.json
```

该命令复算权重和温度诊断、检查当前 RDF 归一化，并重现尚待修复的 Widom 分母问题。它不会生成合格的 c₁/c₂ 标签，也不会启动新的 MD。

如需调用 MACE 模型，再安装对应依赖，并准备目标模型需要的长程计算模块：

```bash
python -m pip install -e ".[mace,test]" scipy
export GRAPH_LONG_RANGE_PATH=/path/to/graph_electrostatics-0.4.0
```

模型文件及 `graph_longrange` 由使用者提供，仓库不包含模型权重。

## 对已有轨迹进行诊断

输入为 ASE 可读取的 `extxyz` 轨迹，以及源势和目标势的模型路径。需先确认轨迹已经平衡、源能量对应实际采样势，并且分析温度与采样设定一致。瞬时动能温度的平均值不能直接替代采样温度。

```python
from pathlib import Path
import ase.io
from sampling.off_polar import OffPolarReweighter, ReweightConfig

frames = list(ase.io.iread("source_prod.xyz", format="extxyz"))
outdir = Path("runs/my_reweight_trial")
if outdir.exists():
    raise FileExistsError(outdir)

# 示例仅用于固定 N/V 的正交周期盒。
# 球壳 RDF 的采样半径须小于最短盒边的一半。
rmax = min(6.0, 0.49 * float(frames[0].cell.lengths().min()))
config = ReweightConfig(temperature_K=300.0, rdf_rmax_A=rmax)
rw = OffPolarReweighter.from_models(
    source_model="/path/MACE-OFF23_medium.model",
    target_model="/path/MACE-POLAR-1-M.model",
    config=config,
)
result = rw.evaluate(frames)
result.write(outdir)
print("weight ESS:", result.ess, "sigma_beta:", result.sigma_beta)
```

`evaluate()` 会对选取的每帧计算目标能量和力。帧中已有 `OFF_energy` 时，程序优先使用它作为源能量；因此不能混用其他势、其他精度或不同参考定义的能量字段。当前代码尚未自动完成所有输入审核，需结合[检查记录](docs/AUDIT_2026-10-23.md)使用。

| 输出 | 内容 |
|---|---|
| `reweight_manifest.json` | 温度、能量差、权重、ESS、线性拟合和模型来源等诊断信息；部分历史文件缺少完整模型哈希 |
| `reweight_frames.csv` | 逐帧能量差、归一化权重和力差 |
| `reweight_diagnostics.png` | 权重与结构统计的诊断图 |

轨迹生成与命令行接口位于 `scripts/` 和 `sampling/cli.py`。当前重加权 CLI 使用默认的 8 Å RDF 半径；小盒子应使用上面的 Python 接口显式设置半径，几何范围的自动校验列在待完成计划中。

## 已有结果与后续工作

| 项目 | 当前状态 |
|---|---|
| Boltzmann 权重、常数偏移不变性及 ESS | 已有测试和现有能量数据的独立复算 |
| RDF 球壳体积归一化 | 已修复；新增理想气体与配位数测试 |
| 96 原子短轨迹重加权 | 36 帧按 334 K 分析时 ESS=3.63；按 300 K 作敏感性复算为3.34。仅为诊断案例，不能据此认证 c₁/c₂ |
| 1152 原子早期检查 | 六个预热帧的 ESS≈1；尚不能据此判定充分平衡后的长轨迹。仓库另有500 ps运行记录，其完成情况以对应结果为准 |
| Widom 与分子理想参考 | 分母错误已复现；加权插入与刚性/柔性参考约定待完成 |
| OZ 网格、有限尺寸与误差 | 网格和真实轨迹流程仍待修正/验收；解析测试通过不能替代这些检查 |
| 目标 POLAR c₁/c₂ 标签 | 尚未完成独立目标参照、观测量不确定度和完整资格审核 |
| 重加权因子方差推导（2026-10-27） | 从权重二阶矩推导 ESS；CV_w=15–21（1,152 原子）、1.1（96 原子）、0.14（气相），对应 ESS 0.2–0.5 %、44 %、98 %。理论推导见 [PDF](docs/reports/REWEIGHT_VARIANCE_2026-10-27.pdf)，四组数据量化见 [数据附录](docs/REWEIGHT_VARIANCE_DATA_2026-10-27.pdf)；Chatterjee–Diaconis 判据 n~exp(KL) 给出 n~1.3e41（Gaussian） |
| 学生→POLAR 重加权 ESS（2026-10-27） | 1,152 原子 σ_β=8.02、ESS 0.24 %（最大单帧权重 91.5 %）；96 原子 ESS≈44 %，气相 98 %。生产尺寸一步重加权判为不可用；详见 [ESS 报告](docs/ESS_STUDENT_TO_POLAR_2026-10-27.md) |

后续顺序是：先修实现与输入约定，再重算已有数据，然后用匹配的 OFF/POLAR 采样验证。若直接重加权仍无法满足观测量精度要求，再实际采样中间混合势或更接近 POLAR 的参考势。BAR/MBAR 需要有重叠的新采样，给原来的同一批帧增加几个能量评分不能补出缺失构型。

## 文档与目录

| 入口 | 内容 |
|---|---|
| [检查记录](docs/AUDIT_2026-10-23.md) | 已复现的问题、证据、适用范围与检查状态 |
| [修复与验证计划](docs/superpowers/plans/2026-10-23-polar-c1c2-validation.md) | 优先级、具体文件、回归测试及采样验收步骤 |
| [实验记录](docs/EXPERIMENTS.md) | 历史数值、RDF修正和采样记录 |
| [PDF阅读入口](docs/reports/README.md) | 理论与实验报告；部分后续审计事项尚未反映到PDF中 |
| [c₁/c₂定义](docs/DIRECT_CORRELATION.md) | 物理定义与现有提取路径，阅读时结合页首审计说明 |
| `sampling/` | 重加权、轨迹、直接关联函数和CLI实现 |
| `tests/` | 数学与实现检查；当前14项测试不等于生产数据资格审核 |
| `validation/` | 反例、解析参照、复算脚本和小型结果 |
| `examples/water96/` | 随仓96原子短轨迹示例及历史诊断 |

理论推导与参考文献见 [docs/THEORY.md](docs/THEORY.md)，其中待修订的覆盖率/ESS解释已在页首标注。大型原始轨迹、模型权重、大型计算输出和软件环境不作为本仓交付内容；随仓短轨迹用于方法检查。
