# 实验报告：MACE-OFF → MACE-POLAR 的重加权与 c1/c2

**日期：** 2026-10-23  
**状态：** 探索性实验，**不是**生产级 c1/c2 结果。  
**结论先行：** 1,000+ 原子的直接重加权 **不可行**（ESS≈1）；96 原子也只是 marginal（ESS≈10%）。c2 的 OZ 反演本身已验证；问题在采样/重叠，不在公式。

---

## 1. 目的

判断能否用便宜的 MACE-OFF 轨迹，加上逐帧 MACE-POLAR 单点能量，通过 Boltzmann 重加权得到 MACE-POLAR 的：

- **c2(r)**：二体直接相关函数（由 \(g(r)\)+OZ）；
- **c1**：一体直接相关函数（均匀体相为常数；非均匀为剖面）。

同时记录当前流程的问题，供老师判断下一步。

## 2. 体系与设置

| 项目 | 设置 |
|---|---|
| 体系 | 水，32 / 384 个分子（96 / 1,152 原子） |
| 盒子 | 96 原子：11.696 Å；1,152 原子：23.39×23.39×35.09 Å |
| 密度 | 0.02 molecules/Å³（约 0.6 g/cm³） |
| 温度 | 300 K |
| 源模型 | **原始 MACE-OFF23 medium**（Symmetrix FP32 引擎 JSON + JIT，不是蒸馏学生） |
| 目标模型 | **MACE-POLAR-1-M**，FP64（PyTorch 单点） |
| 轨迹 | 96 原子 5 ps / 10 ps；1,152 原子 1 ns 尝试（已停止） |
| 时间步 | 0.5 fs |
| 帧间隔 | 0.1 ps 或 1 ps |

> 注意：0.02 molecules/Å³ 在 300 K 接近水的两相区，不是稳定单相液体；这是当前实验的一个物理问题。

## 3. 结果

### 3.1 两力场单点差异（96 原子，81 帧/套，10 ps）

| 量 | MACE-OFF | MACE-POLAR |
|---|---:|---:|
| \(c_1^{\rm ex}\)（绝对值，未对齐） | 80504.257 | 80456.478 |
| \(c_1\) 差 | — | **−47.78**（与 \(-βΔE\) 一致） |
| \(c_2(r)\) 范围 | [−51.2, 226.2] | [−293.3, 1336.8] |

- \(c_1\) 的绝对值被能量参考主导，必须对齐零点；差值 47.78 与 416.6 meV/atom 的偏移一致。
- 两套 \(c_2\) 曲线差异很大，但 96 原子/10 ps 的噪声和有限尺寸占主导，**不能当作真实结构差**。

### 3.2 重加权诊断（96 原子，36 帧）

| 量 | 数值 |
|---|---:|
| ΔE/atom 偏移 | 416.62 meV/atom |
| ΔE/atom 涨落 std | 1.166 meV/atom |
| \(\sigma_\beta=\mathrm{std}(\beta\Delta E)\) | **3.89** |
| ESS | **3.63 / 36 = 10.1%** |
| 判定 | **marginal** |
| 线性 slope / intercept | 0.9452 / −3606.84 eV |
| \(R^2\) / 残差 | 0.9866 / 1.03 meV/atom |
| 力 MAE | 104.7 meV/Å |

### 3.3 重加权 c2 vs 直接 MACE-POLAR c2（81 帧）

| 量 | 数值 |
|---|---:|
| \(\sigma_\beta\) | 3.31 |
| ESS | **2.09 / 81 = 2.6%** |
| c2 直接 POLAR vs OFF 的 RMS | 115.8 |
| c2 直接 POLAR vs 重加权的 RMS | 121.0 |
| 最大差 | 528.7 |

**重加权没有改善一致性，反而略差。** 但 ESS 只有 2.6%，这个比较是“噪声对噪声”，不能证明重加权理论错误——只说明当前数据不够。

### 3.4 1,152 原子：实时 ESS 直接判死

用 `scripts/monitor_ess.py` 实时读取 LAMMPS dump、逐帧算 MACE-POLAR 单点：

| step | ΔE/atom (meV) | \(\sigma_\beta\) | ESS |
|---:|---:|---:|---:|
| 0 | 410.254 | 0.00 | 1/1 |
| 2000 | 414.291 | 127.21 | 1/2 |
| 4000 | 414.857 | 111.87 | 1/3 |
| 6000 | 415.245 | 102.74 | 1/4 |
| 8000 | 415.837 | 98.98 | 1/5 |
| 10000 | 415.806 | 93.83 | 1/6 |

verdict：**collapse**。  
即使 1,000 帧，ESS 仍约 1；ESS 由体系尺寸和势差决定，不由帧数决定。

## 4. 已严谨验证的部分

| 验证 | 结果 |
|---|---|
| 光滑解析 c(r) 的 OZ 反演 | 最大误差 **4.9×10⁻¹³** |
| Percus–Yevick 硬球平滑段 | **2.1×10⁻¹³** |
| 理想气体 c2 | 0 |
| 单元测试 | 12 项通过 |

所以 **c2 的公式和实现是对的**；问题在采样、有限尺寸和重叠。

## 5. 当前实验存在的问题

1. **盒子太小/状态点不对（96 原子）**：\(L=11.7\) Å < \(2r_{\rm cut}=12\) Å；0.02 密度在 300 K 接近两相区。
2. **轨迹太短（10 ps）**：\(g(r)\) 噪声大，c2 摆动到 −293~1337。
3. **c1 绝对值不可直接比较**：被能量参考主导；Widom 只有 50/100 次插入被接受。
4. **ESS 低是本质**：1,152 原子 \(\sigma_\beta\approx94\)，ESS=1；更多帧无效。
5. **重算能量不改变构型**：在 OFF 帧上算 POLAR 能量，\(g(r)\)/c2 仍是 OFF 的。
6. **1,152 原子引擎速度异常**：实测 6.8 steps/s（测试 98 steps/s），1 ns 需 80+ h；已停止。
7. **没有目标参照**：只有 OFF 轨迹，无法最终验证重加权 c2/c1 是否正确。

## 6. 结论与建议

- **直接重加权不适合 1,000+ 原子的 MACE-OFF→MACE-POLAR**；ESS 太小。
- 96 原子只能做 **marginal** 的方法验证，不能作为生产。
- 若要 MACE-POLAR 的 c2/c1：
  1. **直接跑 MACE-POLAR** 短轨迹（100 ps；1,152 原子约 8.3 h）；
  2. 或训练 **ΔV 代理势**（能量+力）再跑 MD；
  3. 非均匀 c1(r) 需要外场下的 POLAR 轨迹 + Euler–Lagrange。
- 若要 PRL 式 c2 泛函：需要**多个密度**的 bulk c2，而不是一条轨迹重加权。

## 7. 复现命令

```bash
# 96 原子双力场 10 ps
python validation/run_forcefield_c1c2.py \
  --structure water96.xyz --off-model MACE-OFF23_medium.model \
  --polar-model MACE-POLAR-1-M.model --ps 10 --equil-ps 1 --frame-ps 0.1 \
  --n-widom 100 --outdir runs/ff_water96

# 重加权 vs 直接 c2
python validation/compare_reweighted_vs_direct.py

# 实时 ESS（任意 LAMMPS dump）
python scripts/monitor_ess.py --dump traj.lammpstrj \
  --off-model MACE-OFF23_medium.model --polar-model MACE-POLAR-1-M.model \
  --temperature 300 --outdir runs/ess_live
```

## 8. 数据与图

- 96 原子重加权诊断：`examples/water96/reweight/reweight_diagnostics.png`
- 重加权 vs 直接 c2：`validation/results/forcefield_c1c2_water96/reweight_vs_direct/reweight_vs_direct.png`
- 1,152 原子实时 ESS：`bench/off23_1ns_water1152_2026-10-23/ess_live/ess_live.json`
- 理论推导：`docs/THEORY.md`、`docs/reports/THEORY_REPORT.pdf`
- 公式+实验合并报告：`docs/reports/EXPERIMENT_REPORT.pdf`
