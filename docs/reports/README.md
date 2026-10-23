# Review package — MACE-OFF → MACE-POLAR c1/c2

**For:** teacher / reviewer  
**Date:** 2026-10-23

## Read in this order

1. **[RESEARCH_REPORT.pdf](RESEARCH_REPORT.pdf)** — 第一章理论、第二章实验的章节式报告（推荐先看）。
2. **[EXPERIMENT_REPORT.pdf](EXPERIMENT_REPORT.pdf)** — 公式 + 当前实验问题（9 页）。
3. **[THEORY_REPORT.pdf](THEORY_REPORT.pdf)** — statistical-mechanics derivation (6 pages).
3. **[../EXPERIMENTS.md](../EXPERIMENTS.md)** — detailed tables, numbers, reproduction commands.
4. **[../THEORY.md](../THEORY.md)** — theory source with references.
5. **[../../examples/water96/README.md](../../examples/water96/README.md)** — 96-atom feasibility run.

## One-paragraph summary

We asked whether a cheap MACE-OFF trajectory can be reweighted to MACE-POLAR
using per-frame energy differences. The reweighting identity and the OZ
inversion are correct (analytic validation: 4.9e-13 for a smooth c(r), 2.1e-13
for Percus–Yevick hard spheres). But the practical overlap fails: 96 atoms
gives ESS 10.1% (marginal), and 1,152 atoms gives ESS = 1 (collapse) because
\(\Delta V\) is extensive and the weights are exponential. A 1 ns MACE-OFF run
does not fix this. For 1,000+ atoms the right routes are direct MACE-POLAR
sampling, a delta-learned surrogate potential, or a PRL-style multi-density
functional — not direct reweighting.

## Key numbers

| Quantity | Value |
|---|---:|
| 96-atom reweight ESS | 3.63/36 = 10.1% (marginal) |
| 96-atom \(\sigma_\beta\) | 3.89 |
| 1,152-atom \(\sigma_\beta\) (live) | 93.8 |
| 1,152-atom ESS (live) | 1.0 (collapse) |
| Energy offset | 416.62 meV/atom |
| Force MAE (bulk water) | 104.7 meV/Å |
| OZ smooth-c validation | 4.9e-13 |

## What we need from the reviewer

- Is direct MACE-POLAR sampling (100 ps–1 ns) acceptable as the reference?
- Should we invest in a \(\Delta V\) surrogate potential for 1,000+ atoms?
- For c1(r), should we run external-field (inhomogeneous) MACE-POLAR
  simulations, or train a PRL-style functional from multiple bulk densities?
