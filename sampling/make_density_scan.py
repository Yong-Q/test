#!/usr/bin/env python3
"""PRL-style density scan for the six molecules.

For each species: temperature T = 1.55 Tc (supercritical), 10 densities
log-spaced between 0.2 and 2.2 rho_c, starting from the 3000-atom dense box
isotropically rescaled to each target density.  Writes LAMMPS data files and
a manifest for sampling/les_batch.py.

Usage:
    python sampling/make_density_scan.py --outroot maceles_density_scan
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from ase.io import read

SIX_ROOT = Path(
    "/workspace/group/shared/bza/symmetrix-polar/bench/q4_maceles_off/six_3000")
# Tc (K), rho_c (molecules/A^3), c2 pair
PRL = {
    "H2O": (647.1, 0.01076, "O O"),
    "NH3": (405.4, 0.00831, "N N"),
    "CH4": (190.6, 0.00608, "C C"),
    "C2H4": (282.3, 0.00459, "C C"),
    "C2H6": (305.3, 0.00407, "C C"),
    "CO2": (304.1, 0.00640, "C O"),
}
NMOL = {"H2O": 1000, "NH3": 750, "CH4": 600, "C2H4": 500,
        "C2H6": 375, "CO2": 1000}
COLUMNS = ["sim_id", "data", "traj", "species", "temperature", "timestep",
           "steps", "dump_every", "density", "c2_pair", "seed", "elements"]


def rescaled_data(src: Path, dst: Path, rho_target: float, n_mol: int) -> float:
    atoms = read(src, format="lammps-data", atom_style="atomic")
    atoms.wrap()
    vol0 = atoms.get_volume()
    rho0 = n_mol / vol0
    scale = (rho0 / rho_target) ** (1.0 / 3.0)
    atoms.set_cell(atoms.cell * scale, scale_atoms=True)
    atoms.wrap()
    dst.parent.mkdir(parents=True, exist_ok=True)
    masses = {1: 12.011, 2: 1.008, 3: 14.007, 4: 15.999}
    L = atoms.cell.lengths()
    assert np.allclose(L, L[0], atol=1e-6)
    with open(dst, "w") as fh:
        fh.write(f"{n_mol}-molecule density-scan frame rho={rho_target:.6g}\n\n")
        fh.write(f"{len(atoms)} atoms\n4 atom types\n\n")
        fh.write(f"0.0 {L[0]:.10f} xlo xhi\n")
        fh.write(f"0.0 {L[0]:.10f} ylo yhi\n")
        fh.write(f"0.0 {L[0]:.10f} zlo zhi\n\nMasses\n\n")
        for t in range(1, 5):
            fh.write(f"{t} {masses[t]:.3f}\n")
        fh.write("\nAtoms # atomic\n\n")
        for i, (s, p) in enumerate(zip(atoms.get_chemical_symbols(),
                                       atoms.get_positions()), 1):
            typ = {"C": 1, "H": 2, "N": 3, "O": 4}[s]
            fh.write(f"{i} {typ} {p[0]:.10f} {p[1]:.10f} {p[2]:.10f}\n")
    return rho0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outroot", default="maceles_density_scan")
    ap.add_argument("--n-densities", type=int, default=10)
    ap.add_argument("--lo", type=float, default=0.2)
    ap.add_argument("--hi", type=float, default=2.2)
    ap.add_argument("--steps", type=int, default=2000000)
    ap.add_argument("--dump-every", type=int, default=1000)
    args = ap.parse_args(argv)
    outroot = Path(args.outroot)
    data_root = outroot / "data"
    rows = []
    for species, (tc, rhoc, pair) in PRL.items():
        temperature = round(1.55 * tc, 1)
        src = SIX_ROOT / species / "data.lammps"
        rhos = np.geomspace(args.lo * rhoc, args.hi * rhoc,
                            args.n_densities)
        for i, rho in enumerate(rhos):
            rho = float(rho)
            dst = data_root / species / f"r{i:02d}_{rho:.6f}.lammps"
            rescaled_data(src, dst, rho, NMOL[species])
            rows.append({
                "sim_id": f"{species}-PRL-T{temperature:g}-r{i:02d}-{rho:.6f}",
                "data": str(dst.resolve()),
                "traj": "", "species": species,
                "temperature": temperature, "timestep": 0.0005,
                "steps": args.steps, "dump_every": args.dump_every,
                "density": f"{rho:.6f}", "c2_pair": pair, "seed": 0,
                "elements": "C H N O",
            })
        print(f"{species}: T={temperature:g} K, rho_c={rhoc:g}, "
              f"{len(rhos)} densities {rhos[0]:.6g}..{rhos[-1]:.6g}")
    manifest = outroot / "density_scan.csv"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
