# Octra HFHE Challenge v2 — current reproducible blocked conclusion

This note summarizes the current local state for the Octra HFHE Challenge v2 worktree at:

`/Users/koala/hfhe_challenge_v2`

It is not a final proof that the challenge is impossible. It is a reproducible statement of what has been checked from the currently public artifacts and why the current public-only route is blocked unless new information, a new structural bug, or a non-generic LPN breakthrough appears.

## Target and artifact identity

Target wallet:

`octC5eR9pLGKbpzTbDgHowkFt8HW7LZYb2gzehzxHamxuAZ`

Local artifact hashes:

```text
5da7f82724838bf7a8c4fe95fbf6d573b621c04c9b2f7ae849545cf60223fbab  secret.ct
1e788edff9dea19a782defae053f3757ccf5edd41cd3e24ae44e1496045e9410  pk.bin
```

Current result:

- Plaintext/private key: **not recovered**.
- Chain state last refreshed: target balance still `500001.000001`, nonce `0`, `has_public_key=false`, `tx_count=5`.
- Official upstream head last refreshed: `019380c97543620091409b0fbf73a8a773a9a0da`.

## Reproduction quick commands

Run from:

```bash
cd /Users/koala/hfhe_challenge_v2
```

Compile/run the main local C++ audits:

```bash
clang++ -std=c++17 -O2 -I pvac_hfhe_cpp/include -I . artifact_wire_audit.cpp -o artifact_wire_audit
./artifact_wire_audit

clang++ -std=c++17 -O2 -I pvac_hfhe_cpp/include -I . pc_commitment_audit.cpp -o pc_commitment_audit
./pc_commitment_audit

clang++ -std=c++17 -O2 -I pvac_hfhe_cpp/include -I . layer_seed_audit.cpp -o layer_seed_audit
./layer_seed_audit

clang++ -std=c++17 -O2 -I pvac_hfhe_cpp/include -I . lpn_binding_full_audit.cpp -o lpn_binding_full_audit
./lpn_binding_full_audit

clang++ -std=c++17 -O2 -I pvac_hfhe_cpp/include -I . candidate_uncheckable_demo.cpp -o candidate_uncheckable_demo
./candidate_uncheckable_demo
```

Run the main Python LPN audits:

```bash
python3 lpn_deep_audit.py
python3 lpn_cross_sample_audit.py
python3 lpn_cross_row_distance_audit.py
python3 lpn_intra_stream_audit.py
python3 lpn_feature_bias_audit.py
python3 lpn_domain_nonce_audit.py
python3 lpn_route_feasibility.py
```

Latest saved outputs are linked by `*_latest.out` symlinks.

## What has been ruled out locally

### 1. Artifact/wire shape issues

Evidence:

- `artifact_wire_audit_latest.out`
- `pc_commitment_audit_latest.out`
- `layer_seed_audit_latest.out`

Summary:

- `secret.ct` parses as a wrapped v2 bundle.
- `22` ciphers, each with `2` base layers, `0` product layers.
- `44` base layers total.
- All `44` PC commitments are unique, non-identity, nonzero, valid Ristretto encodings.
- No product-layer PC, slot-shape, layer-reference, edge-index, or malformed sigma issue detected.
- `R_com` is absent from the v2 wire format. In memory it defaults to identity/zero after deserialization, matching the intended removal of the v1 oracle.
- All base-layer nonces are unique.
- All base-layer ztags are unique and recompute correctly as `prg_layer_ztag(pk.canon_tag, nonce)`.

Conclusion:

No cheap parser, shape, PC reuse, default point, nonce reuse, or ztag derivation route was found.

### 2. Public LPN sample binding issues

Evidence:

- `lpn_binding_full_audit_latest.out`
- `lpn_domain_nonce_audit_latest.out`

Summary:

- Public LPN files: `44`.
- Each filename `ctXX_lY_s0_pvac_prf_r_1.jsonl` matches its metadata `cipher_index/layer_id/slot`.
- Each sample's `seed_ztag`, `nonce_lo_hex`, `nonce_hi_hex`, and `public_T_hex` binds exactly to its named `secret.ct` layer/slot.
- No sample binds to a different target.
- No ambiguous binding.
- Domain is consistently `pvac.prf.r.1`.
- Parameters are consistently `n=4096`, `t=16384`, `tau=1/8`, `row_words=64`.
- No derived domain nonce collision was detected for the checked PRF/noise/Toeplitz domains.

Conclusion:

No ct/layer swap, metadata mismatch, public_T mismatch, duplicate target, or domain/nonce binding mistake was found.

### 3. Simple public LPN structural defects

Evidence:

- `lpn_deep_audit_latest.out`
- `lpn_cross_sample_audit_latest.out`
- `lpn_cross_row_distance_audit_latest.out`
- `lpn_intra_stream_audit_latest.out`
- `lpn_feature_bias_audit_latest.out`
- `lpn_single_bit_scan_latest.out`

Summary:

- Total equations: `720896`.
- Secret dimension: `n=4096`.
- Rank of sampled rows reaches `4096`.
- No duplicate rows across the full set.
- No same-index A-row reuse/complement shortcut across files.
- No adjacent A-row reuse or extreme-distance periodicity.
- No cross-file y-stream reuse/complement.
- No strong `y` coupling to row weight, row index modulo buckets, first/last bytes, or simple combined buckets.
- Single-bit correlation scan does not indicate a weight-1 secret or trivial coordinate leak.

Conclusion:

At the tested surfaces, the public `pvac.prf.r.1` LPN samples behave like dense random LPN samples. No local-Mac structural shortcut was found.

### 4. Generic LPN route feasibility

Evidence:

- `lpn_route_feasibility_latest.out`

Summary:

For `n=4096`, `m=720896`, and `tau=1/8`, a generic pairwise-XOR/BKW style route loses signal too quickly:

- Usable pairwise stages by generous SNR>=5 rule: only up to about `r <= 3`.
- Practical collision buckets eliminate far too few coordinates.
- Eliminating all `4096` coordinates within useful stages would require unrealistically large buckets.

Conclusion:

A generic BKW/LF1 route from the currently published sample count is not a practical local route. Useful progress likely needs a structural bug, leaked additional material, or a significantly stronger LPN method.

### 5. Candidate plaintext offline checking

Evidence:

- `candidate_uncheckable_demo_latest.out`

Summary:

For each wrapped ciphertext, public aggregates have the shape:

```text
T0 = (v + m) * R0
T1 = (-m) * R1
```

For any candidate `v`, one can choose a nonzero mask `m` and witnesses:

```text
R0 = T0 / (v + m)
R1 = T1 / (-m)
```

Then:

```text
T0 / R0 + T1 / R1 = v
```

The demo tested `22` ciphers × `4` representative candidate values = `88` cases, and all `88` fitted.

Conclusion:

The v2 wrapped public equation by itself does not reject wrong plaintext guesses. Without actual `PRF_R` values, a PC opening/blinding, or the removed v1 `R_com` oracle, plaintext candidates are not checkable offline from public files alone.

## Public leak / external state checks

Evidence:

- `github_auth_refresh_latest.out`
- `github_auth_refresh_latest.json`
- `chain_only_refresh_latest.out`
- prior X/Nitter/search outputs such as `x_direct_refresh_latest.out`, `twitter_public_search_latest.out`, `x_guest_search_latest.out`

Summary:

- Authenticated GitHub fork/API scan fetched `28` forks.
- Exact target wallet code search returned only the official README.
- No public fork/code hit contained a validated v2 `priv`, `master_seed`, mnemonic, plaintext, or private key.
- `Iamknownasfesal/octra-hfhe-challenge-recovery` hits are v1/R_com-recovery related, not a v2 target recovery.
- X direct pages confirmed the project-side note that v1 had an unnecessary public artifact and v2 removed that path; no new v2 leak was found.
- Chain state indicates the target funds have not moved in the checked state.

Conclusion:

No public leak or validated third-party v2 recovery was found in the checked public surfaces.


## Reproduction bundle and evidence manifest

Additional reproducibility helpers added after the first version of this note:

- `reproduce_blocked_conclusion.sh` — compiles and runs the core C++ audits and Python LPN diagnostics, saving outputs under `repro_outputs/<UTC timestamp>/`.
- Latest full reproduction output directory: `repro_outputs/20260712_111730/`.
- `evidence_manifest_latest.txt` and `evidence_manifest_latest.json` — SHA-256 manifest for the main artifacts, scripts, saved outputs, and latest reproduction directory.

Latest manifest generation reported:

```text
entries 50
missing 0
```

To regenerate the manifest:

```bash
cd /Users/koala/hfhe_challenge_v2
python3 make_evidence_manifest.py
```

To rerun the core checks:

```bash
cd /Users/koala/hfhe_challenge_v2
./reproduce_blocked_conclusion.sh
```

## Current blocker

The current public artifacts expose only the `pvac.prf.r.1` LPN side target. Decryption requires the full per-layer value:

```text
R = PRF_R1 * PRF_R2 * PRF_R3
```

and the Toeplitz/prf_k-derived material needed by those PRFs. The checked public files do not expose:

- `PRF_R2`
- `PRF_R3`
- Toeplitz stream material
- `sk.prf_k`
- PC opening/blinding `rho`
- plaintext
- mnemonic/private key
- a v2 replacement for the removed v1 `R_com` oracle

## Current conclusion

With the currently public v2 artifacts and the tests above, the solve remains blocked by missing secret PRF material and the apparent hardness of the published LPN samples. The current work has not recovered the plaintext/private key, but it has produced a reproducible negative route audit showing why the straightforward public-only paths tested so far do not solve the challenge.

