# smoke-ui/octra-hfhe-v2-security-assessment reference assessment

## What I pulled
- Local clone: `/Users/koala/octra-hfhe-v2-security-assessment`
- Repo head inspected: `827da3847f3044d255d45ddff994ed0ba9fe65de`
- Upstream repo: https://github.com/smoke-ui/octra-hfhe-v2-security-assessment

## Important conclusion
The smoke-ui assessment is a strong negative-result baseline for **pre-LPN-sample v2**.
It did not recover plaintext/private key and found no direct confidentiality break in wrapper algebra, public field sums, Pedersen PC, subgroup projections, RNG history, parser/canonicalization, tensor features, or proof/integrity side paths.

However, its own `LIMITATIONS.md` says the conclusion must be reassessed if there are:

> Exposed conventional LPN samples linked to the mask secret.

That condition is now true after Octra upstream commit `d9d29d505e2840c0028d7a91a2a8ba59e163b9a4` added `lpn_samples`. Therefore smoke-ui's older statement “V2 provides no LPN samples” is stale for the current challenge route.

## Rerun of reusable smoke-ui tools on current local challenge
Output saved at:

- `/Users/koala/hfhe_challenge_v2/smoke_ui_reference_latest.out`
- `/Users/koala/hfhe_challenge_v2/reference_smoke_ui_refresh_latest.out`

Reusable checks still agree with local prior work:

- 22 ciphertext blocks, 44 base layers, no PROD layers.
- H rank full: 8192/8192.
- No duplicate base nonce/seed/PC.
- Public layer sums distinct: 44/44.
- No exact subgroup/character cancellation observed.
- Length leak only: 301-315 bytes.
- Candidate length commit accepts: 0/15.
- PRF reduced sanity check looks pseudorandom; no direct signal.

## What this changes for our route
Use smoke-ui as evidence that old v2 public-algebra routes are blocked:

1. v1-style public candidate oracle remains absent.
2. PC/Pedersen commitments do not provide candidate verification because blinding is independent.
3. Wrapper algebra leaves one equation with two independent mask inverses per block.
4. Public H/rank/subgroup/tensor/RNG/parser findings are not enough for plaintext recovery.

But do **not** use smoke-ui's old LPN-algorithm conclusion as current: it predates the official `lpn_samples` release. The active path remains the new exposed LPN instance: recover `S` from `y=<A,S> xor e` with n=4096, tau=1/8, m=720896, while continuing to check whether recovered S alone is sufficient or more PRF/Toeplitz material is required.
