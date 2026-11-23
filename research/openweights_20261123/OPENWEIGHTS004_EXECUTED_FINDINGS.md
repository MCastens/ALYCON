# ALYCON OPENWEIGHTS-004 — real pretrained cross-model observability audit

**Executed 2026-11-23.** Four pretrained model archives were measured previously; this is a new, hash-checked, retrospective secondary analysis, **not new pretrained forward inference**.

The existing ALYCON master, historical H/F/W information-geometric kernel, and all previous positive and negative evidence remain frozen. This branch is isolated from `main`.

## Fixed computational comparison

Read historical prediction-only arrays (no joint labels) for four ALYCON methods: mixed, route, route+QK, and probability corrected. At each position define their range as [minimum prediction, maximum prediction]; flag the 20% largest predicted method disagreements within each source/pair; only then compare against the actual archived joint intervention.

Each model includes 16 genuine paired interventions. The source document is the bootstrap unit; duplicated windows with the same document name are grouped.

| Genuine pretrained model | Unique documents | Source-pair-token measurements | True joint within all-four-method interval | Worst-10% error captured by top-20% disagreement | Routing MAE | QK-aware MAE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Pythia-160M | 39 | 138,528 | 60.69% | 58.37% | 0.000795 | 0.000744 |
| Pythia-410M | 39 | 69,264 | 60.38% | 73.58% | 0.001809 | 0.001643 |
| Qwen2.5-0.5B-Instruct | 39 | 69,264 | 60.33% | 71.62% | 0.000338 | 0.000324 |
| SmolLM2-135M | 34 | 120,768 | 62.03% | 73.37% | 0.000648 | 0.000588 |

The existing QK-aware predictor beat the routing-only predictor in all **151 distinct source clusters** across these archives, in source-cluster mean absolute error. This is a reused archive, not independent replication.

**Positive:** operator-level QK correction is consistently valuable under the archived access constraints; cross-method disagreement is a useful risk flag (20% random-selection baseline).

**Negative:** a true joint logit lies outside the convex range of all four scalar predictions in ~38–40% of positions; simple consensus averaging worsened route-only MAE on all four models. Agreement is not a correctness certificate.

This is not evidence of unrecoverable model computation, nor of a new mathematical law: it bounds only convex combinations of these particular scalar forecasts. No whole-vocabulary decisions were measured by this test. No matched-FLOP efficiency claims.

## Pretrained model access

A second isolated experiment is installed at `research/openweights_20261123/hosted_smoke.py` with workflow `.github/workflows/alycon-openweights-20261123.yml`. It pins official GPT-2 weights, requires checkpoint SHA256, verifies QKV parity, performs single-head forecasts, freezes SHA-256, then reveals paired outcomes.

GitHub Actions run [45207829031](https://github.com/MCastens/ALYCON/actions/runs/45207829031) failed before runner steps (empty steps; runner ID 0). Thus **no fresh pretrained execution** or validation is claimed. The exact runner-availability cause has not been established.

## Reproduction/provenance

The complete master-continuation Git bundle, 8 test cases, real-model features, frozen SHA256 manifest, and per-model bootstrap results are preserved in the separately released ALYCON OPENWEIGHTS004 handoff artifact. The source archive files in the user's Library are named `x13_<model>_{predict,reveal}.npz`. Prediction and reveal source hashes are in the frozen and results manifests.

Primary-source methodological overlap is not dismissed: AtP* (arXiv:2403.00745) already recomputes attention softmax for QK corrections; Multiple Mediators (arXiv:2606.27510) formalizes conditional interaction; Mechanistic Tomography (arXiv:2608.19338) explicitly reconstructs intervention responses. ALYCON's prospective state-trajectory reconstruction is a distinct **test target**, not yet proved unique by title comparison.

No changes made to `main`.