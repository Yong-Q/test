# Review package — MACE-OFF → MACE-POLAR c1/c2

> **新增检查：** 请先读[问题记录](../AUDIT_2026-10-23.md)及[修复与验收计划](../superpowers/plans/2026-10-23-polar-c1c2-validation.md)。远端865f203已修复RDF体积并更新部分PDF；Widom、OZ网格和统计审核等修改仍待完成，当前c₁/c₂尚未认证。本次新增审计事项尚未全部反映到PDF中。

**For:** teacher / reviewer  
**Date:** 2026-10-23

## Read in this order

1. **[RESEARCH_REPORT.pdf](RESEARCH_REPORT.pdf)** — 第一章理论、第二章实验的章节式报告（推荐先看）。
2. **[EXPERIMENT_REPORT.pdf](EXPERIMENT_REPORT.pdf)** — 公式 + 当前实验问题（9 页）。
3. **[THEORY_REPORT.pdf](THEORY_REPORT.pdf)** — statistical-mechanics derivation (6 pages).
4. **[../EXPERIMENTS.md](../EXPERIMENTS.md)** — detailed tables, numbers, reproduction commands.
5. **[../THEORY.md](../THEORY.md)** — theory source with references.
6. **[../../examples/water96/README.md](../../examples/water96/README.md)** — 96-atom feasibility run.

## One-paragraph summary

We asked whether a cheap MACE-OFF trajectory can be reweighted to MACE-POLAR
using per-frame energy differences. The reweighting identity and the OZ
inversion are correct (analytic validation: 4.9e-13 for a smooth c(r), 2.1e-13
for Percus–Yevick hard spheres). But the practical overlap fails: 96 atoms
gives ESS 10.1% (marginal); a 1,152-atom 5 ps early check (6 frames, 24 min)
gives ESS = 1. The planned 1 ns run was stopped at 5 ps because the engine
sustains ~6.5 steps/s (≈80 h/ns); a 500 ps production run is in progress.
Extrapolation and the \(\sqrt N\) scaling say more frames do not fix the
overlap. For 1,000+ atoms the right routes are direct MACE-POLAR sampling, a
delta-learned surrogate potential, or a PRL-style multi-density functional —
not direct reweighting.

**Correction (2026-10-23):** the RDF shell volume used a squared-radius
difference instead of the cubic one, inflating \(g(r)\) by ~\(3r/2\). Old c2
numbers (range −293 to 1337) are invalid; corrected c2 is about [−4.8, 3.5]
and the direct-POLAR vs OFF c2 RMS is 0.20 (reweighted 0.48). Code, stored
products, and figures were repaired; 14 unit tests pass.

## Key numbers

| Quantity | Value |
|---|---:|
| 96-atom reweight ESS | 3.63/36 = 10.1% (marginal) |
| 96-atom \(\sigma_\beta\) | 3.89 |
| 1,152-atom run | 24 min 17 s, 10,000 steps × 0.5 fs = 5 ps, 6 dump frames |
| 1,152-atom \(\sigma_\beta\) (live, 6 frames) | 93.8 |
| 1,152-atom ESS (live, 6 frames) | 1.0 (early collapse indicator) |
| Energy offset | 416.62 meV/atom |
| Force MAE (bulk water) | 104.7 meV/Å |
| OZ smooth-c validation | 4.9e-13 |
| c2 direct POLAR vs OFF (corrected) | RMS 0.196 |
| c2 direct POLAR vs reweighted (corrected) | RMS 0.484 |

## What we need from the reviewer

- Is direct MACE-POLAR sampling (100 ps–1 ns) acceptable as the reference?
- Should we invest in a \(\Delta V\) surrogate potential for 1,000+ atoms?
- For c1(r), should we run external-field (inhomogeneous) MACE-POLAR
  simulations, or train a PRL-style functional from multiple bulk densities?
