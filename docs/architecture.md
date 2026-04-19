# Architecture

A one-page map of how data moves through this repo.

---

## Pipeline overview

```
┌─────────────────────────┐
│  data/raw/              │   user-downloaded from Zenodo
│    master_clauses.csv   │   CC-BY 4.0, not committed to git
└─────────────┬───────────┘
              │
              ▼
  scripts/01_prepare_data.py       ─── samples 70 clauses per category
              │                          across 6 selected categories
              ▼
┌─────────────────────────┐
│  data/processed/        │
│    clauses.csv          │   420 rows, committed
└─────────────┬───────────┘
              │
              ▼
  scripts/02_build_embeddings.py   ─── pick backend: tfidf (default)
              │                          or bge-m3 (network required)
              ▼
┌─────────────────────────┐
│  data/embeddings/       │
│    clauses.npy          │   (N, D) float32, L2-normalised
│    metadata.json        │   clause_id order-aligned with rows
│    config.json          │   which backend was used
└─────────────┬───────────┘
              │
              ▼
  scripts/03_compute_index_scores.py  ── scores every clause;
              │                          adds per-category pctile rank
              ▼
┌─────────────────────────┐
│  data/processed/        │
│    scores.csv           │
└─────────────┬───────────┘
              │
              ▼
  scripts/04_export_web_data.py      ── picks 16 demo queries,
              │                         bundles top-k + histogram
              ▼
┌─────────────────────────┐
│  web/src/data/          │
│    precomputed.json     │   <200 KB, the whole UI runs off this
└─────────────┬───────────┘
              │
              ▼
  web/  (Vite + React)               ── static, GitHub Pages
              │
              ▼
        user browser
```

---

## Module layout

### `legal_index/` — the reusable core

| File | Responsibility |
|---|---|
| `types.py` | Dataclasses: `Clause`, `SimilarClause`, `IndexScore`, `QueryResult` |
| `retriever.py` | Exact cosine search with category filter + self-exclude |
| `scorer.py` | Two-dimensional Index Score + level band mapping |
| `classifier.py` | Classification seam (stub; ground-truth in demo) |

Dependencies are kept minimal: numpy + pandas. No torch / no
sentence-transformers at import time — the bge-m3 path is isolated in
`scripts/02_build_embeddings.py`.

### `scripts/` — pipeline stages

Numbered `01_…` through `04_…` for reading order. Each stage:

- takes typed path arguments
- has no hidden state
- is idempotent (re-running overwrites outputs cleanly)
- prints a short summary of what it did

Running them out of order is safe — a missing input file triggers a
clear error message with the command to generate it.

### `web/` — the static frontend

Stack: Vite 5 + React 18 + Tailwind 3 + Recharts 2.

Ships as a single-page app. At boot, imports `precomputed.json` (JSON
import is a native Vite feature, no fetch required). All interaction is
state changes against the pre-bundled query set — no network calls, no
API keys, no cold-start latency.

---

## Deployment topology

```
  localhost :5173      ← `npm run dev` during development
         │
         │  `npm run build`  →  web/dist/
         ▼
  GitHub Pages          ← served from the gh-pages branch
   (lucifer-holly.github.io/legal-clause-index/)
```

The base path in `vite.config.js` is set to `/legal-clause-index/` for
the production build so that `href`s resolve correctly under the
`/legal-clause-index/` GitHub Pages prefix.

---

## What would change at production scale

If this were graduating from portfolio piece to real product:

1. **`data/embeddings/` → real vector DB.** Replace the in-memory
   retriever with Qdrant or Milvus. `ClauseRetriever.search` is the
   single integration seam.
2. **Category filter → learned classifier.** Swap
   `LabelLookupClassifier` for a BERT-fine-tuned clause-type classifier.
3. **Corpus grows.** 420 → 10M+. The algorithm doesn't change; only
   HNSW indices and per-shard scoring do.
4. **Score calibration.** Global `τ` becomes per-category, tuned
   against lawyer-labelled data.
5. **Web backend.** Static bundle → FastAPI + Postgres; per-clause
   scores cached, batch scoring endpoint added.

None of these require throwing away what exists — each is a bounded
replacement of one module.
