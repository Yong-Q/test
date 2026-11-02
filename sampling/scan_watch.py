#!/usr/bin/env python3
"""Watch a running scan: analyse each finished state, then delete its trajectory.

    python -m sampling.scan_watch --root bench/maceles_density_scan --interval 600

Every ``--interval`` seconds it looks for ``samples/<sim_id>/meta.json`` states
that have no ``analysis.json`` yet, runs the full post-processing (c1/c2, all
pair g(r) + anisotropy, structure) and — with ``--prune`` — removes
``run/traj.dump*`` afterwards.  Finished runs are aggregated into
``<out>/scan_summary.csv`` and the figure set.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from sampling.scan_analysis import aggregate, discover_states, run_states


def pending(root: Path, out: Path):
    todo = []
    for sid, sp, temp, rho, state, traj in discover_states(root):
        if not (out / sid / "analysis.json").exists():
            todo.append((sid, state, traj))
    return todo


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--interval", type=float, default=600)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--prune", action="store_true", default=True)
    ap.add_argument("--keep-traj", action="store_true")
    ap.add_argument("--frames", type=int, default=200)
    ap.add_argument("--c2-stride", type=int, default=10)
    ap.add_argument("--pair-frames", type=int, default=20)
    args = ap.parse_args(argv)

    root = Path(args.root)
    out = Path(args.out) if args.out else root / "analysis_scan"
    out.mkdir(parents=True, exist_ok=True)
    prune = args.prune and not args.keep_traj

    while True:
        todo = pending(root, out)
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if todo:
            print(f"[watch {stamp}] {len(todo)} state(s) to process", flush=True)
            run_states(root, out, n_frames=args.frames,
                       c2_stride=args.c2_stride,
                       pairs=True, pair_frames=args.pair_frames,
                       prune_traj=prune)
            aggregate(out)
        else:
            print(f"[watch {stamp}] nothing new", flush=True)
        if args.once:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
