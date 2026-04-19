# Evaluation

Empirical behaviour of the Index Score on the 420-clause CUAD subset, using the
TF-IDF embedding back-end. All numbers are reproducible by running
`scripts/01`–`03` in order with the default seed.

## Headline statistics

| Metric | Value |
|---|---|
| Clauses scored | 420 |
| Score mean | 0.468 |
| Score median | 0.389 |
| Score std | 0.292 |
| Score range | [0.072, 0.953] |

## Level distribution

| Level | Count |
|---|---:|
| Highly Atypical | 92 |
| Atypical | 78 |
| Mixed | 84 |
| Standard | 88 |
| Highly Standard | 78 |

The level bands were calibrated to produce roughly equal-frequency buckets
over the full 420-clause corpus. A real deployment would recalibrate against
lawyer-rated examples; see `methodology.md` §"Calibration".

## Per-category behaviour

| Category | Mean | Std | Min | Max |
|---|---:|---:|---:|---:|
| Governing Law | 0.779 | 0.193 | 0.115 | 0.938 |
| Anti-Assignment | 0.636 | 0.263 | 0.075 | 0.904 |
| Termination For Convenience | 0.465 | 0.245 | 0.107 | 0.953 |
| Cap On Liability | 0.444 | 0.305 | 0.078 | 0.947 |
| Change Of Control | 0.257 | 0.111 | 0.095 | 0.487 |
| Non-Compete | 0.226 | 0.120 | 0.072 | 0.488 |

The per-category means order nicely along an axis of real-world
templatization:

- **Governing Law** (mean 0.779): Short, highly formulaic clauses.
  Many contracts share near-identical phrasings
  (*"This Agreement shall be governed by the laws of the State of …"*).
- **Anti-Assignment** (0.636): Fairly standardized language with small
  stylistic variations.
- **Termination for Convenience** / **Cap on Liability** (0.44–0.47):
  Moderate variance — structure is similar across contracts but terms
  (notice periods, liability caps) differ.
- **Change of Control** / **Non-Compete** (0.23–0.26): Heavily
  negotiated, deal-specific language. Few clauses are truly similar to
  any other clause in the corpus; the distribution is dominated by
  unique drafting.

This ordering matches what lawyers would predict. The Index Score, with no
LLM and no domain fine-tuning, recovers a meaningful semantic property of
the text.

## Qualitative spot-checks

A few highest- and lowest-scoring clauses per category, to give a sense of
what the score actually rewards:

### Cap On Liability

- **Highest (0.947)**
  *"Neither party shall be liable to the other party for any direct,
  indirect, consequential, incidental, special, or punitive damages…"*
  Textbook language; the corpus contains many near-duplicates.

- **Lowest (0.078)**
  *"Insofar as Vendor's obligations under Subsection (b)(i) result from,
  arise out of…"*
  An unusually structured clause cross-referencing other subsections —
  semantically isolated in the corpus.

### Governing Law

- **Highest (0.938)**
  *"This Agreement will be governed and construed in accordance with
  the laws of the State of …"*
  One of the most common phrasings in the entire corpus.

- **Lowest (0.115)**
  *"All disputes arising out of or in connection with this Agreement
  shall be finally …"*
  A dispute-resolution / arbitration clause that got bucketed under
  Governing Law — genuinely different in function from templated
  choice-of-law language. The low score is correct.

### Non-Compete

- **Highest (0.488)** — still only "Mixed" on the global scale, because
  even the most standard Non-Compete is in a category where standardness
  runs low.

  *"Accordingly, you covenant that, except as otherwise approved in
  writing by us, you will…"*

- **Lowest (0.072)**
  *"SRP may not obtain any associate or secondary sponsors whose
  products or concepts …"*
  A sponsorship-specific restriction that happens to live inside a
  Non-Compete slot. Correctly flagged as highly atypical.

## Known limitations

1. **Within-category percentile is more interpretable than absolute
   score.** Two clauses can both be "correctly worded for their category"
   but have very different absolute scores because their categories have
   different intrinsic templatization. The UI therefore displays the
   percentile rank alongside the absolute score.

2. **TF-IDF surfaces lexical matches.** On this demo backend, two clauses
   that share vocabulary score as similar even if they differ in legal
   effect. A production bge-m3 run would reduce but not eliminate this:
   Law Insider's case-study notes (see `references.md`) explicitly call
   out lexical bias as a live problem even for good embeddings.

3. **Short clauses are harder to score.** Clauses shorter than roughly
   80 characters have very few discriminative n-grams; their scores are
   noisier than their longer siblings. We filtered the corpus to ≥60
   characters in `scripts/01_prepare_data.py` as a first-pass guard.

4. **Category is taken as ground truth.** The Law Insider product
   includes a classification step (text → category) before scoring.
   This repo uses CUAD's expert labels directly. `legal_index/classifier.py`
   defines the integration seam; plugging in a learned classifier would
   not require changes to the scorer.

## Reproducibility

All outputs in this document can be regenerated end-to-end:

```bash
python scripts/01_prepare_data.py --per-category 70 --seed 42
python scripts/02_build_embeddings.py --model tfidf
python scripts/03_compute_index_scores.py
```

The default seed (42) fixes clause sampling; with the default TF-IDF
configuration the vocabulary is deterministic; so a second run on the same
machine produces byte-identical CSVs.
