# Reproduction

The packaged reproduction script is:

```bash
./scripts/reproduce_blocked_conclusion.sh
```

It expects the full challenge worktree/artifacts to be available in the same layout used by the local analysis. The selected outputs in this repository are summaries only; large challenge artifacts and bulky generated logs are intentionally not included.

Latest packaged reproduction summary:

```bash
cat evidence/reproduce_summary_20260713_042416.txt
```

Important selected audits:

```bash
python3 audits/r_component_dependency_audit.py
python3 audits/lpn_route_feasibility.py
python3 audits/lpn_cross_sample_audit.py
python3 audits/lpn_feature_bias_audit.py
```

If a candidate private key appears, validate it against the target wallet address before reporting.
