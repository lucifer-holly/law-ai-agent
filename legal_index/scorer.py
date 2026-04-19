"""Two-dimensional Index Score: the core of the Law Insider-style mechanism.

The score answers a single deceptively simple question:

    "Given this clause, how aligned is its phrasing with market standard?"

A clause that looks like many other clauses in the corpus lives in a crowded
neighbourhood and scores HIGH. A clause written in an idiosyncratic way has
few close neighbours and scores LOW. The whole idea is that this judgement
does NOT require an LLM — only a well-indexed corpus and some geometry.

See docs/methodology.md for the motivation, the simplifications taken
relative to a production system, and the directions for future work.
"""

from __future__ import annotations

import numpy as np

from legal_index.retriever import ClauseRetriever
from legal_index.types import Clause, IndexLevel, IndexScore, QueryResult, SimilarClause

# ----- tuned constants ---------------------------------------------------------
# All similarities here are cosine-domain values in [-1, 1]. For our TF-IDF
# corpus, intra-category sims sit around 0.15-0.35, inter-category around 0.08.
# The thresholds below are chosen so the five-bucket bands line up roughly with
# intuition on the existing corpus. They are NOT law-of-physics constants —
# any real deployment would calibrate these against human-labelled examples.
# See docs/methodology.md §"Calibration" for discussion.

DEFAULT_K = 20
DEFAULT_SIM_THRESHOLD = 0.30  # "close enough to count as a neighbour"
DEFAULT_DENSITY_WEIGHT = 0.6
DEFAULT_NEAREST_WEIGHT = 0.4

# Score bands -> labels. Boundaries are empirically calibrated: they map
# approximately to equal-frequency quintiles over our 420-clause CUAD subset,
# so each band has a non-trivial population for the demo. A production
# deployment would recalibrate against lawyer-rated examples.
# See docs/methodology.md §"Calibration" for the exact procedure.
LEVEL_BANDS: list[tuple[float, IndexLevel]] = [
    (0.19, "Highly Atypical"),
    (0.30, "Atypical"),
    (0.49, "Mixed"),
    (0.83, "Standard"),
    (1.01, "Highly Standard"),
]


def _band(score: float) -> IndexLevel:
    for upper, label in LEVEL_BANDS:
        if score < upper:
            return label
    return LEVEL_BANDS[-1][1]


def compute_index_score(
    neighbours: list[SimilarClause],
    k: int = DEFAULT_K,
    sim_threshold: float = DEFAULT_SIM_THRESHOLD,
    density_weight: float = DEFAULT_DENSITY_WEIGHT,
    nearest_weight: float = DEFAULT_NEAREST_WEIGHT,
) -> IndexScore:
    """Combine the two dimensions into a single scalar + a categorical level.

    Dimension 1 — `density`
        Fraction of the top-K neighbours whose similarity is at least
        `sim_threshold`. Bounded in [0, 1].

    Dimension 2 — `nearest`
        Similarity of the top-1 neighbour, clipped to [0, 1]. Captures
        "does at least one clause essentially mirror this one?".

    Final `score` is a convex blend; `density_weight + nearest_weight = 1`.
    """
    if abs(density_weight + nearest_weight - 1.0) > 1e-9:
        raise ValueError("density_weight + nearest_weight must equal 1.0")
    if not neighbours:
        return IndexScore(
            density=0.0,
            nearest=0.0,
            score=0.0,
            level="Highly Atypical",
            k=k,
            sim_threshold=sim_threshold,
        )

    top_k = neighbours[:k]
    if len(top_k) < k:
        # shouldn't happen on our corpus, but be explicit about the degenerate case
        density = sum(1 for n in top_k if n.similarity >= sim_threshold) / k
    else:
        density = sum(1 for n in top_k if n.similarity >= sim_threshold) / k

    nearest = max(0.0, min(1.0, top_k[0].similarity))
    score = density_weight * density + nearest_weight * nearest

    return IndexScore(
        density=density,
        nearest=nearest,
        score=score,
        level=_band(score),
        k=k,
        sim_threshold=sim_threshold,
    )


def score_clause_by_id(
    retriever: ClauseRetriever,
    clause_id: str,
    *,
    k: int = DEFAULT_K,
    sim_threshold: float = DEFAULT_SIM_THRESHOLD,
    within_category: bool = True,
    top_display: int = 5,
) -> QueryResult:
    """Convenience wrapper: fetch the clause by id, score it, bundle a QueryResult.

    Parameters
    ----------
    within_category
        If True (default), restrict the neighbour search to clauses of the
        same `clause_type`. This mirrors Law Insider's "classify first, then
        retrieve" pattern and makes the score meaningful — comparing
        a `Governing Law` clause to `Non-Compete` clauses tells you nothing.
    top_display
        Number of neighbour clauses to include in the returned payload for UI
        display. Independent from `k`, which controls the density statistic.
    """
    # locate the query clause within the retriever
    query_idx = next(
        (i for i, c in enumerate(retriever.clauses) if c.clause_id == clause_id),
        None,
    )
    if query_idx is None:
        raise KeyError(f"clause_id {clause_id!r} not present in retriever")

    query_clause = retriever.clauses[query_idx]
    query_vec = retriever.embeddings[query_idx]
    category = query_clause.clause_type if within_category else None

    neighbours = retriever.search(
        query_vec,
        k=k,
        category=category,
        exclude_clause_id=clause_id,
    )
    index = compute_index_score(
        neighbours,
        k=k,
        sim_threshold=sim_threshold,
    )
    sim_hist = retriever.all_similarities(
        query_vec,
        category=category,
        exclude_clause_id=clause_id,
    )
    return QueryResult(
        query_clause=query_clause,
        index=index,
        top_neighbours=neighbours[:top_display],
        similarity_distribution=[float(x) for x in np.sort(sim_hist)[::-1]],
    )
