"""
03 — Compute Index Scores for every clause in the corpus.

Produces a per-clause score table (used by 04 for exporting demo bundle and by
the evaluation notebook for visualising score distributions).

The per-category percentile rank added here is what the UI uses to communicate
"this clause is in the Xth percentile of market alignment for its category",
which is the most intuitively meaningful number for a legal user.

Input:  data/processed/clauses.csv
        data/embeddings/clauses.npy
Output: data/processed/scores.csv

Usage:  python scripts/03_compute_index_scores.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from legal_index import ClauseRetriever, score_clause_by_id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clauses", default="data/processed/clauses.csv")
    parser.add_argument("--embeddings", default="data/embeddings/clauses.npy")
    parser.add_argument("--output", default="data/processed/scores.csv")
    parser.add_argument("--k", type=int, default=20)
    parser.add_argument("--sim-threshold", type=float, default=0.30)
    args = parser.parse_args()

    retriever = ClauseRetriever.from_files(args.clauses, args.embeddings)
    df = pd.read_csv(args.clauses)

    rows: list[dict] = []
    for cid in df["clause_id"]:
        result = score_clause_by_id(
            retriever,
            cid,
            k=args.k,
            sim_threshold=args.sim_threshold,
        )
        rows.append(
            {
                "clause_id": cid,
                "clause_type": result.query_clause.clause_type,
                "density": result.index.density,
                "nearest": result.index.nearest,
                "score": result.index.score,
                "level": result.index.level,
            }
        )

    scores = pd.DataFrame(rows)

    # Per-category percentile rank: for each clause, what fraction of
    # same-category clauses have a strictly-lower score?
    scores["percentile_in_category"] = (
        scores.groupby("clause_type")["score"]
        .rank(method="average", pct=True)
        .round(3)
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    scores.to_csv(out_path, index=False)

    print(f"Wrote {len(scores)} scores -> {out_path}")
    print("\nScore level distribution:")
    print(scores["level"].value_counts().to_string())
    print("\nPer-category mean score:")
    print(scores.groupby("clause_type")["score"].mean().round(3).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
