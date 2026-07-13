# Octra HFHE v2 Public Audit

Reproducible progress notes for the public Octra HFHE Challenge v2 artifact.

> Current result: **not recovered**. No plaintext, wallet private key, or validated public-only recovery has been found.

## Target

```text
octC5eR9pLGKbpzTbDgHowkFt8HW7LZYb2gzehzxHamxuAZ
```

## Why this repository exists

This repository packages the current public-artifact audit in a clean form: status summaries, reproducible negative checks, selected scripts, and external-reference triage. It intentionally excludes local secrets, tokens, unrelated scratch files, large binary artifacts, and any unverified private-key claims.

## Short conclusion

The public package currently exposes only `pvac.prf.r.1` LPN side samples. Decryption requires the full per-layer mask:

```text
R = PRF_R1 * PRF_R2 * PRF_R3
```

The currently public material does **not** expose `PRF_R2`, `PRF_R3`, `sk.prf_k`, Toeplitz stream material, PC openings, plaintext, or the target wallet private key.

## Contents

- [`status_latest.md`](./status_latest.md) — latest local progress snapshot.
- [`docs/INTRODUCTION.md`](./docs/INTRODUCTION.md) — high-level orientation.
- [`docs/FINDINGS.md`](./docs/FINDINGS.md) — main findings and blockers.
- [`docs/REPRODUCTION.md`](./docs/REPRODUCTION.md) — how to reproduce the packaged checks.
- [`report/HFHE_V2_BLOCKED_CONCLUSION_CURRENT.md`](./report/HFHE_V2_BLOCKED_CONCLUSION_CURRENT.md) — detailed blocked conclusion.
- [`scripts/reproduce_blocked_conclusion.sh`](./scripts/reproduce_blocked_conclusion.sh) — local reproduction runner.
- [`audits/`](./audits/) — selected audit helpers.
- [`evidence/`](./evidence/) — selected output summaries.

## External references checked

- `smoke-ui/octra-hfhe-v2-security-assessment`: useful negative-result baseline, no target recovery.
- `tomismeta/octra-sqlite`: useful wallet-format reference, full-history triage found no target/challenge leak.

## Status

This repository is a progress/audit log, not a solved disclosure. If a candidate plaintext or private key is found later, it should be locally validated against `secret.ct`, `pk.bin`, and the target wallet address before being reported.
