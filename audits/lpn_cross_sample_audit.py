#!/usr/bin/env python3
"""Cross-sample diagnostics for Octra HFHE v2 public LPN samples.

Checks whether per-row y bits across the 44 published LPN instances show
unexpected same-index correlation, repeated y streams, or simple pairwise XOR
bias that could indicate shared noise/stream structure. This does not solve
LPN; it rules out a cheap cross-instance shortcut.
"""

from __future__ import annotations

import glob
import json
import math
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SAMPLE_DIR = ROOT / "upstream_d9d29d5_files" / "lpn_samples"


def load_y(path: Path) -> tuple[dict, bytearray]:
    meta = {}
    ys = bytearray()
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle):
            obj = json.loads(line)
            if line_no == 0 and "format" in obj:
                meta = obj
                continue
            y = int(obj["y"])
            if y not in (0, 1):
                raise ValueError(f"bad y={y} in {path}")
            ys.append(y)
    return meta, ys


def corr_abs(a: bytearray, b: bytearray) -> int:
    if len(a) != len(b):
        raise ValueError("length mismatch")
    # sum +1 for same and -1 for different; absolute correlation count
    same = sum(1 for x, y in zip(a, b) if x == y)
    return abs(2 * same - len(a))


def main() -> None:
    paths = [Path(p) for p in sorted(glob.glob(str(SAMPLE_DIR / "*.jsonl")))]
    if not paths:
        raise SystemExit(f"no samples in {SAMPLE_DIR}")

    metas: list[dict] = []
    yseqs: list[bytearray] = []
    for path in paths:
        meta, y = load_y(path)
        metas.append(meta)
        yseqs.append(y)

    t_values = sorted(set(len(y) for y in yseqs))
    if len(t_values) != 1:
        raise SystemExit(f"mixed y lengths: {t_values}")
    t = t_values[0]
    nfiles = len(paths)

    # Pairwise same-index y-stream correlation.
    pair_stats = []
    identical_pairs = []
    complement_pairs = []
    for i in range(nfiles):
        for j in range(i + 1, nfiles):
            a, b = yseqs[i], yseqs[j]
            same = sum(1 for x, y in zip(a, b) if x == y)
            abs_corr = abs(2 * same - t)
            pair_stats.append((abs_corr, same, i, j))
            if same == t:
                identical_pairs.append((i, j))
            if same == 0:
                complement_pairs.append((i, j))
    pair_stats.sort(reverse=True)

    # For each row index r, count ones across files. If there is a shared per-index
    # bias or noise artifact, these counts may deviate from Binomial(44, 1/2).
    row_counts = []
    for r in range(t):
        row_counts.append(sum(y[r] for y in yseqs))
    mean = sum(row_counts) / t
    var = sum((x - mean) ** 2 for x in row_counts) / t
    min_count, max_count = min(row_counts), max(row_counts)

    # Chi-square against Binomial(nfiles, 1/2) distribution over counts 0..44.
    hist = [0] * (nfiles + 1)
    for c in row_counts:
        hist[c] += 1
    chi = 0.0
    expected = []
    for k in range(nfiles + 1):
        exp = t * math.comb(nfiles, k) / (2 ** nfiles)
        expected.append(exp)
        if exp > 1e-9:
            chi += (hist[k] - exp) ** 2 / exp

    # Per-cipher layer0/layer1 same-index correlation, often the most suspicious
    # case if layer pairs accidentally reused a noise stream.
    by_cipher_layer = {}
    for idx, meta in enumerate(metas):
        by_cipher_layer[(meta.get("cipher_index"), meta.get("layer_id"))] = idx
    layer_pair_lines = []
    for c in sorted({m.get("cipher_index") for m in metas}):
        i = by_cipher_layer.get((c, 0))
        j = by_cipher_layer.get((c, 1))
        if i is None or j is None:
            continue
        same = sum(1 for x, y in zip(yseqs[i], yseqs[j]) if x == y)
        layer_pair_lines.append((abs(2 * same - t), same, c, i, j))
    layer_pair_lines.sort(reverse=True)

    print("# LPN cross-sample audit")
    print(f"files={nfiles} rows_per_file={t} total_y_bits={nfiles*t}")
    print(f"identical_y_pairs={len(identical_pairs)} complement_y_pairs={len(complement_pairs)}")
    print("top_pairwise_abs_corr")
    for abs_corr, same, i, j in pair_stats[:12]:
        print(f"  abs_corr={abs_corr:4d} same={same:5d}/{t} files={paths[i].name} vs {paths[j].name}")
    print("layer0_layer1_same_cipher_top_abs_corr")
    for abs_corr, same, c, i, j in layer_pair_lines[:12]:
        print(f"  cipher={c:02d} abs_corr={abs_corr:4d} same={same:5d}/{t} files={paths[i].name} vs {paths[j].name}")
    print("row_index_across_files_y_count_distribution")
    print(f"  mean={mean:.6f} expected={nfiles/2:.6f} var={var:.6f} expected_var={nfiles/4:.6f}")
    print(f"  min={min_count} max={max_count}")
    print(f"  chi_square_vs_binomial_df44={chi:.3f}")
    nonzero_bins = [(k, v) for k, v in enumerate(hist) if v]
    print("  nonzero_bins=" + ",".join(f"{k}:{v}" for k, v in nonzero_bins))

    # A conservative assessment: no exact y-stream reuse, no extreme pairwise
    # same-index correlation, and row count distribution is near expected.
    max_pair = pair_stats[0][0] if pair_stats else 0
    max_layer_pair = layer_pair_lines[0][0] if layer_pair_lines else 0
    sd_pair = math.sqrt(t)
    print("assessment=" + (
        "no detected cross-file y-stream reuse or same-index correlation shortcut"
        if not identical_pairs and not complement_pairs and max_pair < 5 * sd_pair
        else "manual review recommended: unusual cross-file y correlation"
    ))
    print(f"max_pair_abs_corr={max_pair} sqrt_rows={sd_pair:.3f} max_layer_pair_abs_corr={max_layer_pair}")


if __name__ == "__main__":
    main()
