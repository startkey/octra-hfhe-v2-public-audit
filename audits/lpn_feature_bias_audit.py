#!/usr/bin/env python3
"""Audit public LPN rows for cheap feature/y coupling.

The public samples are LPN equations y=<A,S> xor e.  Generic LPN is still hard,
but an implementation bug can sometimes leak through simple row features: row
weight, row index, low-order bytes, or combinations thereof.  This script scans
all published rows and reports whether any feature bucket has an unusually large
signed y imbalance.
"""

from __future__ import annotations

import math
import pathlib
from collections import defaultdict


ROOT = pathlib.Path(__file__).resolve().parent
SAMPLE_DIR = ROOT / "upstream_d9d29d5_files" / "lpn_samples"


class BucketStats:
    def __init__(self) -> None:
        self.n: dict[object, int] = defaultdict(int)
        self.s: dict[object, int] = defaultdict(int)

    def add(self, key: object, y_sign: int) -> None:
        self.n[key] += 1
        self.s[key] += y_sign

    def top(self, limit: int = 8, min_n: int = 32) -> list[tuple[float, object, int, int]]:
        out: list[tuple[float, object, int, int]] = []
        for k, n in self.n.items():
            if n < min_n:
                continue
            s = self.s[k]
            z = abs(s) / math.sqrt(n)
            out.append((z, k, n, s))
        out.sort(reverse=True, key=lambda x: x[0])
        return out[:limit]

    def max_z(self, min_n: int = 32) -> float:
        t = self.top(1, min_n=min_n)
        return t[0][0] if t else 0.0


def extract_y_a(line: str) -> tuple[int, str]:
    # Row format is compact and stable: {"i":0,"y":1,"a":"..."}
    yp = line.find('"y":')
    if yp < 0:
        raise ValueError("missing y")
    y = int(line[yp + 4])
    ap = line.find('"a":"', yp)
    if ap < 0:
        raise ValueError("missing a")
    ap += 5
    aq = line.find('"', ap)
    if aq < 0:
        raise ValueError("bad a")
    return y, line[ap:aq]


def scan() -> None:
    feature_names = [
        "weight_bucket32", "weight_mod2", "weight_mod4", "weight_mod8", "weight_mod16", "weight_mod32",
        "row_index_mod2", "row_index_mod4", "row_index_mod8", "row_index_mod16", "row_index_mod32",
        "row_index_mod64", "row_index_mod128", "row_index_mod256", "row_index_mod512", "row_index_mod1024",
        "first_byte", "last_byte", "first_u16_mod256", "last_u16_mod256",
        "first_last_byte_xor", "weight_mod16__row_mod16", "weight_mod16__first_byte_mod16",
    ]
    stats = {name: BucketStats() for name in feature_names}
    per_file = []
    total_rows = 0
    total_y_sign = 0
    weight_sum = 0
    weight_min = 10**9
    weight_max = -1

    for path in sorted(SAMPLE_DIR.glob("*.jsonl")):
        rows = 0
        y1 = 0
        file_sign = 0
        file_weight_sum = 0
        with path.open(encoding="utf-8") as f:
            next(f)
            for line in f:
                y, a_hex = extract_y_a(line)
                b = bytes.fromhex(a_hex)
                w = int.from_bytes(b, "little").bit_count()
                y_sign = 1 if y else -1
                idx = rows
                rows += 1
                y1 += y
                file_sign += y_sign
                total_rows += 1
                total_y_sign += y_sign
                weight_sum += w
                file_weight_sum += w
                weight_min = min(weight_min, w)
                weight_max = max(weight_max, w)

                first = b[0]
                last = b[-1]
                first_u16 = b[0] | (b[1] << 8)
                last_u16 = b[-2] | (b[-1] << 8)

                stats["weight_bucket32"].add(w // 32, y_sign)
                for m in (2, 4, 8, 16, 32):
                    stats[f"weight_mod{m}"].add(w % m, y_sign)
                for m in (2, 4, 8, 16, 32, 64, 128, 256, 512, 1024):
                    stats[f"row_index_mod{m}"].add(idx % m, y_sign)
                stats["first_byte"].add(first, y_sign)
                stats["last_byte"].add(last, y_sign)
                stats["first_u16_mod256"].add(first_u16 & 0xff, y_sign)
                stats["last_u16_mod256"].add(last_u16 & 0xff, y_sign)
                stats["first_last_byte_xor"].add(first ^ last, y_sign)
                stats["weight_mod16__row_mod16"].add((w % 16, idx % 16), y_sign)
                stats["weight_mod16__first_byte_mod16"].add((w % 16, first & 15), y_sign)
        per_file.append((path.name, rows, y1, file_sign, file_weight_sum / rows))

    print("# LPN feature-bias audit")
    print(f"files={len(per_file)} rows={total_rows}")
    print(f"global_y1={(total_rows + total_y_sign)//2} global_y0={(total_rows - total_y_sign)//2} global_y_sign={total_y_sign} global_z={abs(total_y_sign)/math.sqrt(total_rows):.3f}")
    print(f"weight_avg={weight_sum/total_rows:.6f} weight_min={weight_min} weight_max={weight_max}")
    print("\n# top feature bucket z-scores")
    max_seen = 0.0
    max_name = ""
    total_buckets = 0
    for name in feature_names:
        total_buckets += len(stats[name].n)
        top = stats[name].top(limit=5, min_n=32)
        if top and top[0][0] > max_seen:
            max_seen = top[0][0]
            max_name = name
        print(f"## {name} buckets={len(stats[name].n)} max_z={stats[name].max_z():.3f}")
        for z, key, n, s in top:
            print(f"  z={z:.3f} key={key!r} n={n} signed_y={s}")
    print("\n# per-file y/weight summary")
    for name, rows, y1, sign, wavg in per_file:
        print(f"{name} rows={rows} y1={y1} signed_y={sign} z={abs(sign)/math.sqrt(rows):.3f} weight_avg={wavg:.3f}")
    # A rough multiple-testing sanity line.  For independent Gaussian buckets,
    # sqrt(2 log N) is the expected extreme scale; 8 is deliberately conservative.
    expected_extreme = math.sqrt(2.0 * math.log(max(total_buckets, 2)))
    print("\n# assessment")
    print(f"total_feature_buckets={total_buckets} expected_random_extreme_z≈{expected_extreme:.3f} observed_max_z={max_seen:.3f} observed_max_feature={max_name}")
    if max_seen < 8.0:
        print("assessment=no strong y/row-feature coupling detected at conservative z<8 threshold")
    else:
        print("assessment=investigate unusually large y/row-feature coupling above")


if __name__ == "__main__":
    scan()
