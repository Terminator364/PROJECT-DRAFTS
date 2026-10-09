# MATRICE Cloud Research Kernel V0.1 — SHADOW ONLY

Integration architecture only; not a trained, field-validated or profitable betting model.

## Source-informed foundations
- Matrice V2.5 portable engine: feature engineering, Poisson O1.5 formula, market from O/U2.5 and explicit route/scope.
- V2.9 beta: prematch status gate, timezone-aware timestamps, aliases, source validation, frozen-core adapter.
- ISI 2.0: dedicated rules/explainability branch; no assertion that 70 rules were statistically validated.
- MAXV M5X: SHA, exact transaction state, evidence governance, OOS and non-promotion of negative results.

No old `joblib` object is imported or deserialized. This package does not include private source code or datasets.

## API
`from matrice_unified.core import predict, evaluate, paired_compare, poisson_over15, market_ou25_to_over15`

`predict(packet)` takes timestamped provenance for every feature and precomputed legacy-model probability. It fails closed on data leakage, invalid fixtures, missing policy or unknown inputs. Results always report `SHADOW` or `ABSTAIN`.

`evaluate(records)` evaluates precomputed predictions (not train/test by itself) for hit rate, coverage, Brier, log-loss, ECE and ROI only when every selected observation has odds. Use only protected OOS datasets with frozen decisions and audit digests.

## Run locally in cloud sandbox
`python -m unittest discover -s tests -v`

## Remaining before true legacy engine fusion
1. Verify original model artifacts and SHA manifests, including full V2.8 `v28_core.py` and licensed data.
2. Complete adapter-invocation in safe isolated environments; do not unpickle untrusted artifacts.
3. Align match IDs, predictions, universe, odds, timestamps and labels across routes.
4. Reproduce historic ROUTED_15 benchmark and confirm no provenance gaps.
5. Evaluate true out-of-sample with preregistered test and scientific approval; never assert improved precision before the paired results exist.

Current status: **ENGINEERING-SHADOW / NO MODEL PROMOTION / NO REAL-MONEY EXECUTION**.