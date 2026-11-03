#!/usr/bin/env python3
"""Upload finished trajectories to Zenodo in bounded batches.

Keeps the local disk small without hammering a slow link: each pass uploads at
most ``--batch`` trajectories, deletes a local file only after Zenodo returns
2xx for its final commit, and records what was uploaded so a rerun never
re-sends the same file.

    export ZENODO_TOKEN=...
    python -m sampling.zenodo_batch_traj --root bench/maceles_density_scan \
        --record-id 23901522 --batch 3 --watch 3600

One file per pass is uploaded as ``trajectories/<sim_id>.dump.gz``.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from sampling.zenodo_upload import upload


def finished(root: Path, state_file: Path):
    done = json.loads(state_file.read_text()) if state_file.exists() else {}
    out = []
    for meta in sorted(root.rglob("samples/*/meta.json")):
        state = meta.parent
        if "samples_old" in str(state) or "_legacy" in str(state):
            continue
        sid = state.name
        if sid in done:
            continue
        traj = state / "run" / "traj.dump.gz"
        if not traj.exists():
            traj = state / "run" / "traj.dump"
        if traj.exists():
            out.append((sid, traj))
    return out, done


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True)
    ap.add_argument("--record-id", required=True)
    ap.add_argument("--batch", type=int, default=3)
    ap.add_argument("--watch", type=float, default=0)
    ap.add_argument("--state", default=None)
    args = ap.parse_args(argv)

    root = Path(args.root)
    state_file = Path(args.state) if args.state else root / ".zenodo_traj.json"
    while True:
        try:
            todo, done = finished(root, state_file)
        except Exception as exc:                 # noqa: BLE001
            print(f"[traj] scan error: {type(exc).__name__}: {exc}")
            time.sleep(max(60, args.watch))
            continue
        todo = todo[:max(1, args.batch)]
        print(f"[traj {time.strftime('%H:%M:%S')}] {len(todo)} to upload "
              f"({len(done)} done)")
        for sid, traj in todo:
            key = f"trajectories/{sid}.dump.gz" if traj.suffix == ".gz" \
                else f"trajectories/{sid}.dump"
            ok = upload(args.record_id, key, traj)
            if ok:
                traj.unlink()
                done[sid] = {"key": key, "bytes": None}
                state_file.write_text(json.dumps(done, indent=2))
                print(f"[traj] uploaded and removed {traj}")
            else:
                print(f"[traj] keeping {traj} (upload failed)")
        if args.watch <= 0:
            return 0
        time.sleep(args.watch)


if __name__ == "__main__":
    raise SystemExit(main())
