# Introduction

This project tracks a public analysis of Octra HFHE Challenge v2.

The challenge asks solvers to recover the plaintext/private key associated with the target wallet. The local work here focuses on reproducible public-artifact analysis: parsing the artifact, verifying public LPN sample bindings, checking structural shortcuts, monitoring public GitHub/X sources, and documenting dead ends.

Current result: the target plaintext/private key has not been recovered.

The most important active blocker is that public files expose only `pvac.prf.r.1` LPN side samples, while decryption needs the complete per-layer mask `R = PRF_R1 * PRF_R2 * PRF_R3` plus secret-keyed Toeplitz material.
