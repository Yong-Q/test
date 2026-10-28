#!/usr/bin/env python3
"""Plot the 501-frame MACE-OFF23 and MACE-POLAR potential-energy fluctuations."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "validation/off23_500ps_water1152_2026-10-23"
OUT = PKG / "potential_fluctuations_501"

rows = []
with open(PKG / "frames_501_total_energies.csv") as fh:
    for r in csv.DictReader(fh):
        rows.append(r)
t = np.array([float(r["time_ps"]) for r in rows])
n = int(rows[0]["n_atoms"])
e_off = np.array([float(r["E_OFF_total_eV"]) for r in rows])
e_pol = np.array([float(r["E_POLAR_total_eV"]) for r in rows])
dU = e_pol - e_off

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "legend.fontsize": 8,
    "axes.linewidth": 0.8,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "savefig.dpi": 300,
})
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#4D4D4D"

fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.8))
a = ax[0]
a.plot(t, (e_off - e_off.mean()) / n * 1e3, lw=0.8, color=BLUE,
       label="MACE-OFF23")
a.plot(t, (e_pol - e_pol.mean()) / n * 1e3, lw=0.8, color=ORANGE,
       label="MACE-POLAR")
a.set_xlabel("time (ps)")
a.set_ylabel("(E - <E>)/N (meV atom$^{-1}$)")
a.set_title("Potential-energy fluctuations")
a.legend(frameon=False)
a.grid(alpha=0.2)

b = ax[1]
b.plot(t, dU, lw=0.7, color=GREY, label="$E_{POLAR}-E_{OFF}$")
b.axhline(dU.mean(), color=BLUE, ls="--", lw=0.9,
          label=f"mean {dU.mean():.2f} eV")
b.axhspan(dU.mean() - dU.std(), dU.mean() + dU.std(), color=BLUE,
          alpha=0.12, label=f"$\\pm1\\sigma$ = {dU.std():.3f} eV")
b.set_xlabel("time (ps)")
b.set_ylabel("$\\Delta U$ (eV, whole box)")
b.set_title("Target-minus-source energy difference")
b.legend(frameon=False, fontsize=7.5)
b.grid(alpha=0.2)

for a_ in ax:
    a_.spines["top"].set_visible(False)
    a_.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig(OUT.with_suffix(".png"), bbox_inches="tight")
fig.savefig(OUT.with_suffix(".pdf"), bbox_inches="tight")
print("wrote", OUT.with_suffix(".png"))
print(f"mean dU {dU.mean():.4f} eV  std {dU.std():.4f} eV  "
      f"per atom std {dU.std()/n*1e3:.4f} meV/atom")
