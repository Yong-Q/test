#!/usr/bin/env python3
"""Mirror a scan's analysis output to a Zenodo deposition, continuously.

Zenodo records are immutable once published, but files can be added to an
*unpublished* deposition at any time.  This keeps one draft deposition open and
uploads every new/changed file under ``analysis_scan/`` (c1/c2, pair and
intramolecular statistics, figures, summaries).  Publish once at the end — or
publish periodically and bump the version.

    export ZENODO_TOKEN=...            # scopes: deposit:write, deposit:actions
    python -m sampling.zenodo_upload --root bench/maceles_density_scan/analysis_scan \
        --deposition-id 123456 --watch 600

    # first run without --deposition-id creates the draft and prints its id
    # add --publish when you want the DOI (record becomes read-only)

Environment:
    ZENODO_TOKEN   personal access token (required, never commit it)
    ZENODO_API     default https://zenodo.org/api
                   use https://sandbox.zenodo.org/api while testing

Files are addressed by their path relative to --root, so re-uploads overwrite
the same key instead of duplicating.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import requests

DEFAULT_METADATA = {
    "title": "MACELES PRL density scan — c1/c2 and pair correlations",
    "upload_type": "dataset",
    "description": (
        "Bulk molecular dynamics with the MACELES (MACE + Latent Ewald "
        "Summation) engine: c1/c2, partial g(r) with anisotropy, "
        "intramolecular geometry, molecular axes, COM/MSD, per state."
    ),
    "creators": [{"name": "Qiu, Yong"}],
    "keywords": ["cDFT", "MACELES", "latent Ewald summation", "c1/c2", "g(r)"],
    "access_right": "open",
    "license": "cc-by-4.0",
}


def _api() -> str:
    return os.environ.get("ZENODO_API", "https://zenodo.org/api").rstrip("/")


def _headers() -> dict:
    token = os.environ.get("ZENODO_TOKEN")
    if not token:
        raise SystemExit("ZENODO_TOKEN is not set "
                         "(create one at zenodo.org/account/settings/applications)")
    return {"Authorization": f"Bearer {token}"}


def create_deposition(metadata=None) -> dict:
    r = requests.post(f"{_api()}/depositions",
                      json={"metadata": metadata or DEFAULT_METADATA},
                      headers=_headers(), timeout=60)
    r.raise_for_status()
    dep = r.json()
    print(f"[zenodo] created deposition {dep['id']} (draft)")
    return dep


def get_deposition(dep_id) -> dict:
    r = requests.get(f"{_api()}/depositions/{dep_id}",
                     headers=_headers(), timeout=60)
    r.raise_for_status()
    return r.json()


def update_metadata(dep_id, metadata):
    r = requests.put(f"{_api()}/depositions/{dep_id}",
                     json={"metadata": metadata},
                     headers=_headers(), timeout=60)
    if r.status_code >= 400:
        print(f"[zenodo] metadata update failed: {r.status_code} {r.text[:200]}")
    return r.ok


def upload_file(bucket: str, local: Path, key: str) -> bool:
    url = f"{bucket.rstrip('/')}/{key}"
    with open(local, "rb") as fh:
        r = requests.put(url, data=fh, headers=_headers(), timeout=600)
    if r.status_code >= 400:
        print(f"[zenodo] upload failed {key}: {r.status_code} {r.text[:200]}")
        return False
    print(f"[zenodo] uploaded {key} ({local.stat().st_size/1e6:.1f} MB)")
    return True


def publish(dep_id):
    r = requests.post(f"{_api()}/depositions/{dep_id}/actions/publish",
                      headers=_headers(), timeout=120)
    if r.status_code >= 400:
        print(f"[zenodo] publish failed: {r.status_code} {r.text[:300]}")
        return False
    print(f"[zenodo] published {dep_id}: {r.json().get('links', {}).get('doi')}")
    return True


def pending_files(root: Path, uploaded: dict):
    """Yield (key, path) for files that are new or whose size/mtime changed."""
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        key = str(p.relative_to(root))
        sig = (p.stat().st_size, int(p.stat().st_mtime))
        if uploaded.get(key) != sig:
            yield key, p, sig


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", help="directory to mirror (required unless --single-file)")
    ap.add_argument("--deposition-id")
    ap.add_argument("--watch", type=float, default=0,
                    help="seconds between scans (0 = one pass)")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--metadata", help="JSON file with Zenodo metadata")
    ap.add_argument("--state", default=None,
                    help="upload bookkeeping (default <root>/.zenodo_state.json)")
    ap.add_argument("--single-file", help="upload just this file (with --key)")
    ap.add_argument("--key", help="remote key for --single-file")
    ap.add_argument("--delete-after", action="store_true",
                    help="delete --single-file once the upload returns 2xx")
    args = ap.parse_args(argv)

    if args.single_file:
        if not args.deposition_id or not args.key:
            raise SystemExit("--single-file needs --deposition-id and --key")
        dep = get_deposition(args.deposition_id)
        if dep.get("status") == "published":
            raise SystemExit("deposition is published (read-only)")
        src = Path(args.single_file)
        ok = upload_file(dep["links"]["bucket"], src, args.key)
        if ok and args.delete_after:
            src.unlink()
            print(f"[zenodo] deleted local {src}")
        return 0 if ok else 1

    if not args.root:
        raise SystemExit("--root is required unless --single-file is used")
    root = Path(args.root)
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")
    meta = DEFAULT_METADATA
    if args.metadata:
        meta = json.loads(Path(args.metadata).read_text())
    state_path = Path(args.state) if args.state else root / ".zenodo_state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}

    dep_id = args.deposition_id or state.get("deposition_id")
    if dep_id:
        dep = get_deposition(dep_id)
        print(f"[zenodo] reusing deposition {dep_id} ({dep.get('status', 'draft')})")
        if dep.get("status") == "published":
            print("[zenodo] WARNING: the deposition is published (read-only); "
                  "create a new version to add files")
    else:
        dep = create_deposition(meta)
        dep_id = dep["id"]
        state["deposition_id"] = dep_id
        state_path.write_text(json.dumps(state, indent=2))
        update_metadata(dep_id, meta)
    bucket = dep["links"]["bucket"]

    while True:
        uploaded = state.setdefault("files", {})
        n = 0
        for key, path, sig in pending_files(root, uploaded):
            if key.startswith(".zenodo_state"):
                continue
            if upload_file(bucket, path, key):
                uploaded[key] = sig
                n += 1
                state_path.write_text(json.dumps(state, indent=2))
        print(f"[zenodo {time.strftime('%H:%M:%S')}] {n} file(s) uploaded")
        if args.publish:
            publish(dep_id)
            return 0
        if args.watch <= 0:
            return 0
        time.sleep(args.watch)


if __name__ == "__main__":
    raise SystemExit(main())
