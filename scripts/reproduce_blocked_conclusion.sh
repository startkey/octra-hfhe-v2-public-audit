#!/usr/bin/env bash
set -euo pipefail

# Reproduce the core public-only negative checks for Octra HFHE Challenge v2.
# Run from /Users/koala/hfhe_challenge_v2 or any checkout containing the same files.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

OUT_DIR="repro_outputs/$(date -u +%Y%m%d_%H%M%S)"
mkdir -p "$OUT_DIR"

echo "# HFHE v2 blocked-conclusion reproduction"
echo "root=$ROOT"
echo "out_dir=$OUT_DIR"
echo

have() { command -v "$1" >/dev/null 2>&1; }

if ! have clang++; then
  echo "missing clang++; install Xcode command line tools or another C++17 compiler" >&2
  exit 2
fi

if ! have python3; then
  echo "missing python3" >&2
  exit 2
fi

echo "## artifact hashes" | tee "$OUT_DIR/00_hashes.out"
if have sha256sum; then
  sha256sum secret.ct pk.bin | tee -a "$OUT_DIR/00_hashes.out"
else
  shasum -a 256 secret.ct pk.bin | tee -a "$OUT_DIR/00_hashes.out"
fi

compile_run() {
  local src="$1"
  local bin="$OUT_DIR/${src%.cpp}"
  local out="$OUT_DIR/${src%.cpp}.out"
  echo
  echo "## $src"
  clang++ -std=c++17 -O2 -I pvac_hfhe_cpp/include -I . "$src" -o "$bin"
  "$bin" | tee "$out"
}

run_py() {
  local src="$1"
  local out="$OUT_DIR/${src%.py}.out"
  echo
  echo "## $src"
  python3 "$src" | tee "$out"
}

compile_run artifact_wire_audit.cpp
compile_run pc_commitment_audit.cpp
compile_run layer_seed_audit.cpp
compile_run lpn_binding_full_audit.cpp
compile_run candidate_uncheckable_demo.cpp

run_py lpn_domain_nonce_audit.py
run_py lpn_deep_audit.py
run_py lpn_cross_sample_audit.py
run_py lpn_cross_row_distance_audit.py
run_py lpn_intra_stream_audit.py
run_py lpn_feature_bias_audit.py
run_py lpn_route_feasibility.py

echo
echo "## summary grep"
grep -R "^assessment=\|^assessment \|assessment:" "$OUT_DIR"/*.out || true

echo
echo "reproduction outputs saved in $OUT_DIR"
