# Findings

## Positive findings

- The target wallet and artifact identity are tracked in `status_latest.md`.
- `secret.ct` and `pk.bin` match the expected critical artifact hashes in the local integrity check.
- The latest full reproduction run completed and saved negative-check outputs.
- `tomismeta/octra-sqlite` was inspected as a wallet-format reference; no target/challenge leak was found in worktree or full git history.

## Negative findings / blocked routes

- No recovered plaintext or private key found.
- No public `R_com` oracle comparable to v1.
- No PC commitment reuse/default/decode anomaly found.
- No layer nonce/ztag reuse found.
- No LPN filename/metadata/public_T binding mismatch found.
- No repeated row, same-index reuse/complement, y-stream reuse, simple feature bias, or local-Mac generic BKW route found.
- Candidate plaintexts remain offline-uncheckable from the public wrapped equations alone.

## Current blocker

Public material exposes only `pvac.prf.r.1` LPN samples. Current public data does not include `PRF_R2`, `PRF_R3`, `sk.prf_k`, secret-keyed Toeplitz stream material, PC openings, plaintext, or target private key.
