# off-polar-reweight

## For review (2026-10-23)

- [Chapter report (PDF, theory + experiments)](docs/reports/RESEARCH_REPORT.pdf) — 第一章理论，第二章测试。
- [Experiment report (PDF, 9 pages)](docs/reports/EXPERIMENT_REPORT.pdf) — formulas + current experiment problems.
- [Theory report (PDF, 6 pages)](docs/reports/THEORY_REPORT.pdf) — statistical-mechanics derivation.
- [Review package index](docs/reports/README.md) — one-paragraph summary and key numbers.
- [Detailed experiments](docs/EXPERIMENTS.md) — tables, caveats, reproduction commands.

**Bottom line:** the reweighting identity and OZ inversion are correct, but
the practical overlap fails: 96 atoms gives ESS 10.1% (marginal); 1,152 atoms
gives ESS = 1 (collapse). A 1 ns MACE-OFF run does not fix this. For 1,000+
atoms use direct MACE-POLAR sampling, a delta-learned surrogate, or a
PRL-style multi-density functional.


Reweight a **source** machine-learning interatomic potential trajectory
(MACE-OFF) to a **target** potential (MACE-POLAR) by free-energy perturbation
/ importance sampling, and diagnose whether the phase-space overlap is
sufficient.

The method is exact in the infinite-sample limit:

\[
\langle O\rangle_{\rm target}
=
\frac{\sum_i O_i\,e^{-\beta\Delta V_i}}
     {\sum_i e^{-\beta\Delta V_i}},
\qquad
\Delta V_i=V_{\rm target}(x_i)-V_{\rm source}(x_i).
\]

A constant energy offset cancels in the normalized weights.  In practice the
exponential average is limited by the overlap:

\[
\sigma_\beta=\mathrm{std}(\beta\Delta V),\qquad
\mathrm{ESS}=\frac{(\sum_i w_i)^2}{\sum_i w_i^2}.
\]

For \(\sigma_\beta\gtrsim3\) the weights are dominated by a few frames and
direct reweighting collapses.  The repository therefore reports
\(\sigma_\beta\), ESS, a linear `slope, intercept` fit, and a verdict instead of silently
returning a biased average.

## Why this repository exists

The workflow was developed for Symmetrix-Polar, where MACE-POLAR is the exact
but expensive teacher (128.99 µs/atom/step at 5,184 atoms) and MACE-OFF is a
cheap source.  The package is kept standalone so the interface can be reused
with other source/target ASE calculators.

## Install

```bash
python -m pip install -e ".[mace,test]"
```

MACE-POLAR requires `graph_longrange` on `PYTHONPATH`; set

```bash
export GRAPH_LONG_RANGE_PATH=/path/to/graph_electrostatics-0.4.0
```

The package reads model paths from the caller; no model is bundled.

## Python interface

```python
import ase.io
from sampling.off_polar import OffPolarReweighter, ReweightConfig

frames = list(ase.io.iread("off_traj.xyz", format="extxyz"))
rw = OffPolarReweighter.from_models(
    source_model="/path/MACE-OFF23_medium.model",
    target_model="/path/MACE-POLAR-1-M.model",
    config=ReweightConfig(temperature_K=300.0, stride=1),
)
result = rw.evaluate(frames)
print(result.as_dict()["verdict"], result.ess, result.sigma_beta)
result.write("out/")
```

`OffPolarReweighter` is calculator-agnostic: pass any ASE `Calculator`
instances to the constructor if you do not use MACE.

The output `reweight_manifest.json` contains model paths and SHA-256 hashes,
temperature, per-frame ΔV, \(\sigma_\beta\), ESS, the `slope,intercept` fit, force MAE,
and a verdict (`usable`, `marginal`, `collapse`).  `reweight_frames.csv` and
`reweight_diagnostics.png` are written alongside it.

## CLI

```bash
# 1) source trajectory (MACE-OFF)
off-polar-run \
  --structure water96.xyz \
  --model /path/MACE-OFF23_medium.model \
  --out off_traj.xyz \
  --temperature 300 --ps 5 --equil-ps 0.5 --frame-ps 0.1

# 2) target labels + reweighting diagnostics
off-polar-reweight \
  --traj off_traj.xyz \
  --source-model /path/MACE-OFF23_medium.model \
  --polar-model /path/MACE-POLAR-1-M.model \
  --temperature 300 --outdir out/
```

The thin wrappers in `scripts/` call the same functions if the package is not
installed.

## Frame count for 1 ns

- 1 fs timestep, save every **1 ps → 1,000 frames** (default for ensemble
  means and RDFs);
- every **0.5 ps → 2,000 frames** (better for reweighting diagnostics and
  shorter correlation times);
- the limiting quantity for reweighting is **ESS**, not the nominal frame
  count.  2,000 frames do not rescue an overlap problem.

## Feasibility result

A 96-atom water probe (36 production frames) gives
\(\Delta E/\mathrm{atom}=416.6\pm1.17\) meV, \(\sigma_\beta=3.89\),
ESS = 3.6/36 = 10.1 %, verdict **marginal**; the linear fit has
\(R^2=0.987\) but a 1.03 meV/atom residual.  Extrapolating
\(\sigma_\beta\propto\sqrt N\) gives 14.3 at 1,296 atoms and 28.6 at
5,184 atoms, so direct reweighting is not usable at production sizes.
Full detail: [`examples/water96/README.md`](examples/water96/README.md).

## Direct correlation functions (PRL c1/c2)

The PRL (Dijkman et al., PRL 134, 056103 (2025)) uses c1 and c2 as the
one- and two-body direct correlation functions, not as linear-fit
coefficients.  `sampling/direct_correlation.py` extracts c2(r) from a bulk
g(r) through the Ornstein–Zernike relation and provides a Widom-insertion
utility for the constant c1.  See [`docs/DIRECT_CORRELATION.md`](docs/DIRECT_CORRELATION.md).
The reweighting manifest's `linear.slope` and `linear.intercept_eV` are a
different object and are named accordingly.

## Validation

- `validation/harmonic.py`: exact 1D and N-mode harmonic tests.  The
  reweighted moments converge to the analytic values, and
  \(\sigma_\beta=x_0\sqrt{\beta k N}\) reproduces the measured collapse as
  \(N\) grows.  Results: `validation/results/harmonic_validation.json` and
  `harmonic_validation.png`.
- `tests/`: 12 unit tests for weights, ESS, the linear fit, observable
  reweighting, and the OZ inversion (smooth analytic c and PY hard spheres).
- `validation/direct_correlation.py`: OZ inversion against analytic c(r);
  smooth case error 4.9e-13, PY hard-sphere smooth part 2.1e-13.

## Theory and citations

See [`docs/THEORY.md`](docs/THEORY.md).  Core references:

1. R. W. Zwanzig, *J. Chem. Phys.* **22**, 1420 (1954).
2. G. M. Torrie, J. P. Valleau, *J. Comput. Phys.* **23**, 187 (1977).
3. A. M. Ferrenberg, R. H. Swendsen, *Phys. Rev. Lett.* **63**, 1195 (1989).
4. C. H. Bennett, *J. Comput. Phys.* **22**, 245 (1976).
5. M. R. Shirts, J. D. Chodera, *J. Chem. Phys.* **129**, 124105 (2008).
6. S. Majumdar et al., *Reweighting free energy profiles between universal
   machine learning interatomic potentials for fast consensus building*,
   arXiv:2605.15630 (2026).

## Limits

- The estimator is exact only for equilibrated source samples with overlap.
- A global intercept offset cancels; a global slope is only an effective-temperature
  rescaling.  The residual \(\delta V(x)\) must be retained.
- For large \(N\), \(\sigma_\beta\) grows approximately as \(\sqrt{N}\); direct
  reweighting should be expected to fail even when per-atom errors look small.
- The mean-energy-gap/Gaussian approximations correct free-energy profiles, not
  arbitrary ensemble averages with a single global constant.
