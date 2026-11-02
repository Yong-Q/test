#!/usr/bin/env bash
# Build the `symmpolar-engine` CUDA wheel from a symmetrix-xl checkout.
#
#   SYMMPOLAR_CUDA_ARCH=80 scripts/../packaging/symmpolar-engine/build_wheel.sh [SYMMETRIX_DIR]
#
# Compiles Kokkos-CUDA + the Symmetrix python extension; needs nvcc (CUDA
# 12.x) but no GPU.  ~15-30 min.  The wheel is written to ./dist.
set -euo pipefail

HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
REPO=$(cd -- "$HERE/../.." && pwd -P)
SYMMETRIX_DIR=${1:-${SYMMETRIX_DIR:-$REPO/../symmetrix-xl}}
CUDA_ARCH=${SYMMPOLAR_CUDA_ARCH:-80}
PY=${PY:-python3}
OUT=${OUT:-$REPO/dist}

if [[ ! -f "$SYMMETRIX_DIR/symmetrix/pyproject.toml" ]]; then
    echo "not a symmetrix-xl checkout: $SYMMETRIX_DIR" >&2
    exit 1
fi

PATCH=$REPO/../symmetrix-polar/engine/maceles-les/0001-maceles-complete-LES-integration-with-charge-respons.patch
if [[ -f "$PATCH" ]]; then
    cd "$SYMMETRIX_DIR"
    if git apply --check "$PATCH" >/dev/null 2>&1; then
        git apply "$PATCH"; echo "applied LES patch"
    elif git apply --reverse --check "$PATCH" >/dev/null 2>&1; then
        echo "LES patch already applied"
    else
        echo "WARNING: LES patch neither applies nor is applied" >&2
    fi
fi

BACKUP=$(mktemp)
cp "$SYMMETRIX_DIR/symmetrix/pyproject.toml" "$BACKUP"
trap 'cp "$BACKUP" "$SYMMETRIX_DIR/symmetrix/pyproject.toml"; rm -f "$BACKUP"' EXIT

cp "$HERE/pyproject.toml" "$SYMMETRIX_DIR/symmetrix/pyproject.toml"
NVCC_WRAPPER="$SYMMETRIX_DIR/libsymmetrix/external/kokkos/bin/nvcc_wrapper"
if [[ ! -x "$NVCC_WRAPPER" ]]; then
    echo "nvcc_wrapper not found at $NVCC_WRAPPER" >&2
    exit 1
fi
export PATH="$(dirname "${CUDACXX:-/usr/local/cuda/bin/nvcc}"):$PATH"
mkdir -p "$OUT"
echo "== building symmpolar-engine for sm_${CUDA_ARCH} =="
SYMMPOLAR_CUDA_ARCH="$CUDA_ARCH" \
SYMMPOLAR_NVCC_WRAPPER="$NVCC_WRAPPER" \
CUDACXX="${CUDACXX:-$(command -v nvcc || true)}" \
    "$PY" -m pip wheel "$SYMMETRIX_DIR/symmetrix" \
        --no-deps --no-build-isolation -w "$OUT"

ls -lh "$OUT"/symmpolar_engine-*.whl
echo "install: pip install $OUT/symmpolar_engine-*.whl"
