# ALYCON: operator observability continuation — 23 Nov 2026

This research branch remains isolated from main. The full executed code, source-level hashes, separate forecast/reveal records, adverse controls, integration tests, and incremental Git bundle are archived in the user’s ChatGPT ALYCON Work transfer (local master commit c2d33cb; base 7aa5a97).

## UNIQUE-QK-007
For previously archived genuine pretrained hidden-state joint interventions, decompose a predicted QK-aware correction against the span of two other correction vectors. Conditional extra oracle energy after the other directions, on ten source-disjoint held-out documents per model:

- Pythia-160M 27.24% vs source-shuffled measured-vector control 0.20%
- Pythia-410M 14.28% vs 0.96%
- Qwen2.5-0.5B-Instruct 16.28% vs 0.41%
- SmolLM2-135M 19.19% vs 2.12%

Additional real-vector pair- and token-position-shuffle controls and independent QR parity confirmed the arithmetic. This is a privileged oracle representation **diagnostic**, not a new prospective correction, a native causal isolation of QK, or a proof of a universal information law.

An initial prediction-freeze implementation hashed the joint archive before reveal; although it extracted no labels, it violated strict phase isolation. The old evidence was preserved. The corrected version re-freezes and reproduces the result without opening or hashing joint arrays before reveal.

**Negative:** the prediction-only independence fraction did not consistently forecast per-document improvement (Spearman -0.35, +0.56, -0.24, +0.31). No reliable selector.

## QK-SPLIT-008
New label-free forecast construction: separate the existing QK-aware direction into its orthogonal new and already-expressible components. Candidate full tensors were hashed and frozen before any joint-outcome access.

Across the same four pretrained archives, the unique component explains 56.3%, 92.4%, 78.1%, 82.3% of the existing QK correction's observed squared-error reduction, respectively. The full original QK correction is better in aggregate; this is a computational accounting result rather than an improved predictor. The parts' SSE improvements add by the standard Pythagorean identity.

**Validation:** 100 existing integration tests + 5 UNIQUE-QK tests + 3 QK-SPLIT tests passed in separate completed runs, 108 total. The longer combined process stalled, so no single uninterrupted combined pass is claimed.

**Scope:** these are new analyses of genuine historical pretrained outcomes, not newly executed pretrained forward passes. They preserve ALYCON's original H/F/W kernel, causal C15 formation/transport, physical-system experiments, and all prior positive/negative evidence. Source-disjoint evaluation is retrospective; only native open-weight interventions with independent parity can identify which boundary created the missing direction.

**Pretrained forward blocker:** the public GPT-2 checkpoint is not mounted and direct model-host access is blocked. GitHub Actions run 45207829031 failed before allocating a hosted runner. No fresh checkpoint-based joint outcomes were obtained.

## Primary-source method overlaps
AtP* https://arxiv.org/abs/2403.00745 (QK attention fix; §5.1 explicitly evaluates rank, not magnitude accuracy);
Anthropic attention QK feature interactions https://transformer-circuits.pub/2025/attention-qk/index.html;
cross-layer interaction decomposition https://arxiv.org/abs/2608.03629;
Mechanistic Tomography https://arxiv.org/abs/2608.19338 (measurement sufficiency and conditional interactions).

These works are close on individual operations; an implementation-level parity audit remains necessary before claiming novelty or equivalence.