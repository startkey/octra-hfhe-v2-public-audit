# Octra HFHE Challenge v2 — public progress notes

This repository records a reproducible public-artifact analysis of Octra HFHE Challenge v2.

Target wallet:

```text
octC5eR9pLGKbpzTbDgHowkFt8HW7LZYb2gzehzxHamxuAZ
```

Current result: **plaintext/private key not recovered**.

## Latest status

See [`status_latest.md`](./status_latest.md).

## Main conclusion

Current public artifacts expose only `pvac.prf.r.1` LPN side samples. Decryption requires complete per-layer:

```text
R = PRF_R1 * PRF_R2 * PRF_R3
```

The current public package does not expose `PRF_R2`, `PRF_R3`, `sk.prf_k`, Toeplitz stream material, PC openings, plaintext, or target private key.

## Reproduction

The main local reproduction command is:

```bash
./scripts/reproduce_blocked_conclusion.sh
```

The latest saved reproduction summary is in [`evidence/reproduce_summary_20260713_042416.txt`](./evidence/reproduce_summary_20260713_042416.txt).

## External references checked

- `smoke-ui/octra-hfhe-v2-security-assessment`: used as a negative-result baseline; no target recovery.
- `tomismeta/octra-sqlite`: wallet-format reference only; full-history grep found no target/challenge leak.

## Notes

This repository intentionally omits local secrets, GitHub tokens, unrelated local files, and bulky generated artifacts. It is a progress/audit log, not a solved key disclosure.
