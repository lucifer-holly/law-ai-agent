"""
04 — Export a self-contained JSON bundle for the static web demo.

Picks 18 "demo queries" spanning the score spectrum across the 6 categories,
precomputes top-k neighbours + distributions for each, and ships the lot as a
single <=200KB JSON file that the frontend fetches at boot. The entire UI
runs off this one file — no backend, no API keys, no runtime compute.

Input:  data/processed/clauses.csv
        data/processed/scores.csv  (from scripts/03)
        data/embeddings/clauses.npy
        data/embeddings/config.json
Output: web/src/data/precomputed.json

Usage:  python scripts/04_export_web_data.py
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from legal_index import ClauseRetriever, score_clause_by_id
from legal_index.scorer import LEVEL_BANDS, DEFAULT_K, DEFAULT_SIM_THRESHOLD


# Demo query selection strategy: for each of the 6 categories, pick one clause
# from three zones of the score distribution (low / mid / high), so the UI
# exposes visitors to the full range of the Index. This gives ~18 queries
# total, the right density for a "click through 5-10 of them" demo session.
#
# We sample rather than hand-pick: reproducibility beats cherry-picking for
# a portfolio piece, because reviewers can re-run the scripts and see the
# same selection. The seed is fixed.
ZONE_DEFINITIONS = {
    "low": (0.00, 0.30),   # Atypical / Highly Atypical
    "mid": (0.30, 0.60),   # Mixed
    "high": (0.60, 1.01),  # Standard / Highly Standard
}
SAMPLES_PER_ZONE_PER_CATEGORY = 1
SEED = 7


def select_demo_queries(scores: pd.DataFrame) -> list[str]:
    rng = np.random.default_rng(SEED)
    selected: list[str] = []
    for category in scores["clause_type"].unique():
        cat_scores = scores[scores["clause_type"] == category]
        for zone_name, (lo, hi) in ZONE_DEFINITIONS.items():
            in_zone = cat_scores[(cat_scores["score"] >= lo) & (cat_scores["score"] < hi)]
            if len(in_zone) == 0:
                # Category doesn't populate this zone; skip rather than force.
                # e.g. Governing Law barely has any "low-zone" clauses.
                continue
            n = min(SAMPLES_PER_ZONE_PER_CATEGORY, len(in_zone))
            picks = rng.choice(in_zone["clause_id"].values, size=n, replace=False)
            selected.extend(picks.tolist())
    return selected


def build_payload(
    retriever: ClauseRetriever,
    scores: pd.DataFrame,
    clauses_df: pd.DataFrame,
    embedding_config: dict,
) -> dict:
    demo_ids = select_demo_queries(scores)
    scores_by_id = scores.set_index("clause_id")

    queries: list[dict] = []
    for cid in demo_ids:
        result = score_clause_by_id(
            retriever,
            cid,
            k=DEFAULT_K,
            sim_threshold=DEFAULT_SIM_THRESHOLD,
            top_display=5,
        )
        pctile = float(scores_by_id.loc[cid, "percentile_in_category"])
        queries.append(
            {
                "clause_id": result.query_clause.clause_id,
                "clause_type": result.query_clause.clause_type,
                "contract_name": result.query_clause.contract_name,
                "text": result.query_clause.text,
                "index_score": {
                    "density": round(result.index.density, 3),
                    "nearest": round(result.index.nearest, 3),
                    "score": round(result.index.score, 3),
                    "level": result.index.level,
                    "percentile_in_category": round(pctile, 3),
                },
                "top_neighbours": [
                    {
                        "clause_id": n.clause.clause_id,
                        "text": n.clause.text,
                        "similarity": round(n.similarity, 3),
                        "contract_name": n.clause.contract_name,
                    }
                    for n in result.top_neighbours
                ],
                # Full similarity histogram against the category cohort; truncate
                # to 3 decimals to shrink the JSON payload without loss of meaning.
                "similarity_distribution": [
                    round(x, 3) for x in result.similarity_distribution
                ],
            }
        )

    # Per-category aggregate statistics for the "market overview" panel in the UI
    by_cat: dict[str, dict] = {}
    for cat in scores["clause_type"].unique():
        sub = scores[scores["clause_type"] == cat]["score"]
        by_cat[cat] = {
            "n": int(len(sub)),
            "mean": round(float(sub.mean()), 3),
            "median": round(float(sub.median()), 3),
            "p25": round(float(sub.quantile(0.25)), 3),
            "p75": round(float(sub.quantile(0.75)), 3),
        }

    return {
        "meta": {
            "embedding_backend": embedding_config.get("backend"),
            "embedding_dim": embedding_config.get("dim"),
            "n_clauses_total": int(len(clauses_df)),
            "n_demo_queries": len(queries),
            "n_categories": int(clauses_df["clause_type"].nunique()),
            "k": DEFAULT_K,
            "sim_threshold": DEFAULT_SIM_THRESHOLD,
            "level_bands": [
                {"upper": upper, "label": label} for upper, label in LEVEL_BANDS
            ],
        },
        "categories": list(clauses_df["clause_type"].unique()),
        "category_stats": by_cat,
        "queries": queries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clauses", default="data/processed/clauses.csv")
    parser.add_argument("--embeddings", default="data/embeddings/clauses.npy")
    parser.add_argument("--embedding-config", default="data/embeddings/config.json")
    parser.add_argument("--scores", default="data/processed/scores.csv")
    parser.add_argument("--output", default="web/src/data/precomputed.json")
    args = parser.parse_args()

    retriever = ClauseRetriever.from_files(args.clauses, args.embeddings)
    scores = pd.read_csv(args.scores)
    clauses_df = pd.read_csv(args.clauses)
    with open(args.embedding_config) as f:
        emb_config = json.load(f)

    payload = build_payload(retriever, scores, clauses_df, emb_config)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, separators=(",", ":"), ensure_ascii=False)

    size_kb = out_path.stat().st_size / 1024
    print(f"Wrote {out_path} ({size_kb:.1f} KB)")
    print(f"  {len(payload['queries'])} demo queries")
    print(f"  {payload['meta']['n_clauses_total']} total clauses in corpus")
    print(f"  embedding backend: {payload['meta']['embedding_backend']}")

    # Sanity-check level distribution across demo queries
    level_counts: dict[str, int] = {}
    for q in payload["queries"]:
        level_counts[q["index_score"]["level"]] = level_counts.get(q["index_score"]["level"], 0) + 1
    print("\nDemo query level distribution:")
    for level, n in sorted(level_counts.items()):
        print(f"  {level:<20} {n}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
