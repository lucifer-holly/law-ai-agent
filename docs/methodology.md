# Methodology

This document is the canonical reference for how the Index Score is
computed, why it's computed that way, and what simplifications were
taken relative to a production-grade system.

It's intentionally longer than a typical "how to run the demo" section —
the point of this repo is to think clearly, not just to ship a UI.

---

## The quantity we want to estimate

For a query clause `q` belonging to category `C`, the Index Score tries
to answer one question:

> **Among clauses of the same category in the corpus, how close is `q`
> to the centre of mass of "what the market actually writes"?**

A clause that reads like many other clauses in its category sits in a
dense semantic neighbourhood. A clause drafted in an idiosyncratic way
sits in a sparse one. Both properties are directly observable from the
geometry of the embedding space.

Crucially, **no generative reasoning is required to extract this
signal**. This is the key architectural claim the repo makes, inherited
from studying Law Insider's published design.

---

## Definition

Given a corpus of `N` clauses, each embedded into a `d`-dimensional
unit vector $v_i \\in \\mathbb{R}^d$ with $\\|v_i\\| = 1$:

**Step 1 — filter by category.**  Let $S_C = \\{ i : \\text{category}(i) = C \\}$
be the set of same-category clauses. Compute cosine similarity
between the query $q$ and every $v_i \\in S_C$:

$$s_i = v_q \\cdot v_i \\quad \\text{for } i \\in S_C \\setminus \\{q\\}$$

**Step 2 — the two statistics.**

- `density(q)` — fraction of the top-K neighbours whose similarity
  meets a threshold:
  $$\\text{density}(q) = \\frac{|\\{i \\in \\text{top}_K : s_i \\geq \\tau\\}|}{K}$$
- `nearest(q)` — similarity of the single closest neighbour,
  clipped into $[0, 1]$:
  $$\\text{nearest}(q) = \\max(0, \\min(1, s_{(1)}))$$

**Step 3 — blend into a scalar.**
$$\\text{score}(q) = w_d \\cdot \\text{density}(q) + w_n \\cdot \\text{nearest}(q)$$
with $w_d + w_n = 1$ (default: 0.6 / 0.4).

**Step 4 — map to a five-level spectrum** via fixed bands:

| Score range | Level |
|---|---|
| `[0.00, 0.19)` | Highly Atypical |
| `[0.19, 0.30)` | Atypical |
| `[0.30, 0.49)` | Mixed |
| `[0.49, 0.83)` | Standard |
| `[0.83, 1.00]` | Highly Standard |

**Step 5 — per-category percentile rank.** For UI interpretation,
rank the score among same-category clauses:

$$\\text{pctile}_C(q) = \\Pr_{i \\in S_C}\\big[\\text{score}(i) < \\text{score}(q)\\big]$$

This is the number we actually foreground in the UI, because it's the
only one that's comparable across categories with different intrinsic
templatization levels.

Current defaults used throughout:
`K = 20`, `τ = 0.30`, `w_d = 0.6`, `w_n = 0.4`.

---

## Why density + nearest (and not just one of them)?

The two statistics answer subtly different questions:

- **`nearest` alone** would say "is there *any* clause that mirrors
  this one?". Good at catching templated phrasings, bad at detecting
  clauses that are *roughly* typical — a clause 0.30 from its nearest
  neighbour looks identical to a clause 0.50 from its nearest neighbour
  on this axis alone.
- **`density` alone** would say "is this phrasing in a busy
  neighbourhood?". Good at detecting crowd-typicality, bad at giving
  credit to clauses that have one near-perfect twin amid otherwise
  loose neighbours.

Blending both catches two distinct kinds of "standard":

1. **Templated standard** — high `nearest`, moderate `density`. A
   clause lifted from a widely copied template.
2. **Common-pattern standard** — moderate `nearest`, high `density`.
   A clause whose language pattern is diffusely shared across many
   drafters.

A clause that scores high on *both* is unambiguously market-standard.
A clause that scores high on *neither* is genuinely atypical.

---

## Why pre-filter by category?

Comparing a *Governing Law* clause to *Non-Compete* clauses is not
informative — they live in different parts of the embedding space for
trivial lexical reasons. Pre-filtering keeps the statistics meaningful.

This is exactly Law Insider's pattern: classify the clause type first,
then search within that bucket. In the demo corpus the CUAD labels are
ground truth. In production the classifier would be a discriminative
model (BERT fine-tune, or a logistic regression over embeddings) —
`legal_index/classifier.py` documents the integration seam.

---

## Calibration

The threshold `τ = 0.30` and the five-level band boundaries were chosen
**empirically, once**, by scoring all 420 clauses and looking at the
distribution:

- `τ` was raised from an initial 0.15 because at 0.15 the density
  statistic collapsed to ≈ 1 for almost every clause (any same-category
  neighbour meets the bar). At 0.30, density meaningfully separates
  "crowded neighbourhood" from "sparse neighbourhood" across categories.
- The five level bands were set at the empirical quintile boundaries of
  the global score distribution, so each band has a non-trivial
  population in the demo.

This is **not a rigorous calibration procedure**. A real deployment
would:

1. Collect human-rated examples (e.g. lawyer rankings of
   "looks standard" vs "looks unusual") for a sample of clauses.
2. Fit `(τ, w_d, w_n, band_boundaries)` to maximise agreement with the
   human ratings.
3. Recalibrate per category — a single global τ is a known
   simplification.

Per-category calibration is left as Future Work. Given the
per-category similarity distributions differ substantially (in the CUAD
subset: `Governing Law` intra-category median 0.455, `Non-Compete` median
0.201), a properly tuned system would use a category-specific τ, not a
global one.

---

## What this does NOT model

Worth listing explicitly, because each is a place a real system
would have to do more work:

- **Structural alignment** — Law Insider's real score considers
  whether "subject to X" / "notwithstanding Y" / exception clauses
  are present in the expected positions. I only use surface semantic
  similarity.
- **Frequency weighting** — a phrase that appears in 10,000 contracts
  is more "standard" than one appearing in 10, even if local
  similarities are the same. Our corpus is too small (420 clauses) for
  this to matter, but at scale it's a missing axis.
- **Confidence intervals** — the score is deterministic; it should
  carry uncertainty when the neighbour count is small or the nearest
  distance is near the band boundary.

---

## Embedding backend choice

The pipeline supports two backends with identical downstream contracts:

| | TF-IDF (default) | bge-m3 |
|---|---|---|
| Dimension | 8,192 | 1,024 |
| Size on disk | ~14 MB | ~3 MB |
| Build time (420 clauses, CPU) | ~3 s | ~30 s (+ one-time 2 GB download) |
| Semantic depth | lexical / stemming-like | full contextual semantics |
| Produces demo bundle | ✓ | ✓ |
| Best for | portability, CI, shippable demo | true production quality |

The TF-IDF backend uses character n-grams (3–5) rather than word
n-grams. This is deliberate: character n-grams recover stem-sharing
across closely related legal phrasings (*liability / liabilities*,
*assign / assignee / assignable*) without an explicit stemmer, and they
survive OCR noise — a property that matters on EDGAR-sourced documents.

On this 420-clause corpus, the TF-IDF backend already achieves
same-category vs cross-category similarity separation of roughly 2–3×
(intra-category mean 0.13–0.32, inter-category 0.08–0.11). bge-m3
sharpens this further but the shape of the Index Score output is
qualitatively similar.

This is a deliberately *honest* fallback — the repo does not pretend
the demo is running bge-m3. The `config.json` shipped alongside the
embeddings records which backend was used.

---

## Reading guide for reviewers

If you only read two files after this one, read:

1. `legal_index/scorer.py` — the algorithm. ~150 lines, heavily
   commented, no dependencies beyond numpy.
2. `scripts/04_export_web_data.py` — how the offline pipeline meets
   the static UI. The entire frontend runs off this one JSON.
