#!/usr/bin/env python3
"""Reproducible audit of which secret material remains needed after public R1 LPN samples.

This does not attempt to solve LPN.  It checks the pinned source and the published
sample headers to answer a narrower question: would recovery of the published
`pvac.prf.r.1` LPN secret alone let a solver recompute a decryption mask R?
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PVAC = ROOT.parent / "pvac_hfhe_cpp_v2" / "include" / "pvac" / "crypto" / "lpn.hpp"
SAMPLES = ROOT / "upstream_d9d29d5_files" / "lpn_samples"
SER = ROOT / "source" / "pvac_artifact_serialize.hpp"


def must(pattern: str, text: str, label: str) -> bool:
    found = bool(re.search(pattern, text, flags=re.S))
    print(f"{label}={int(found)}")
    return found


def main() -> int:
    lpn = PVAC.read_text(encoding="utf-8")
    serializer = SER.read_text(encoding="utf-8")
    headers = []
    for path in sorted(SAMPLES.glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as handle:
            headers.append(json.loads(handle.readline()))

    domains = Counter(h.get("dom") for h in headers)
    print("# HFHE v2 R-component dependency audit")
    print(f"sample_files={len(headers)}")
    print("sample_domains=" + json.dumps(dict(sorted(domains.items())), sort_keys=True))

    derives_from_prf_k = must(
        r"for\s*\(\s*auto\s+x\s*:\s*sk\.prf_k\s*\)\s*sha256_acc_u64",
        lpn,
        "derive_aes_key_uses_sk_prf_k",
    )
    r1_r2_r3 = must(
        r"Fp\s+r1\s*=\s*prf_R_core\(.*?Dom::PRF_R1.*?"
        r"Fp\s+r2\s*=\s*prf_R_core\(.*?Dom::PRF_R2.*?"
        r"Fp\s+r3\s*=\s*prf_R_core\(.*?Dom::PRF_R3",
        lpn,
        "prf_R_requires_r1_r2_r3",
    )
    toeplitz_keyed = must(
        r"derive_aes_key\(pk,\s*sk,\s*seed,\s*Dom::TOEP,\s*toep_key,\s*toep_nonce\)",
        lpn,
        "toeplitz_stream_uses_secret_derived_key",
    )
    secret_serializes_prf_k = must(
        r"serialize_seckey.*?for\s*\(\s*int\s+i\s*=\s*0;\s*i\s*<\s*4;\s*\+\+i\s*\)\s*w\.u64\(sk\.prf_k\[i\]\)",
        serializer,
        "seckey_format_contains_prf_k",
    )

    only_r1 = set(domains) == {"pvac.prf.r.1"}
    print(f"published_domains_only_r1={int(only_r1)}")
    print(
        "assessment="
        + (
            "published R1 rows do not expose the complete mask derivation: R2/R3 and "
            "the secret-keyed Toeplitz stream remain unavailable"
            if derives_from_prf_k and r1_r2_r3 and toeplitz_keyed and secret_serializes_prf_k and only_r1
            else "unexpected source/artifact mismatch; manual review required"
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
