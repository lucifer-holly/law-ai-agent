"""Typed records passed between pipeline stages.

Using dataclasses (not dicts) so the shape of data flowing through the system
is explicit and refactor-friendly. Any downstream consumer (scoring, export,
UI contract) can rely on these types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

IndexLevel = Literal[
    "Highly Atypical",
    "Atypical",
    "Mixed",
    "Standard",
    "Highly Standard",
]


@dataclass(frozen=True)
class Clause:
    """A single clause extracted from the CUAD corpus."""

    clause_id: str
    clause_type: str
    contract_name: str
    text: str


@dataclass(frozen=True)
class SimilarClause:
    """A neighbour returned by the retriever, along with its cosine similarity."""

    clause: Clause
    similarity: float  # cosine similarity in [-1, 1]; for L2-normalised vectors == dot product


@dataclass(frozen=True)
class IndexScore:
    """The two-dimensional market-alignment score for a given query clause.

    Fields
    ------
    density
        Fraction of the top-K neighbours whose similarity >= SIM_THRESHOLD.
        Interpreted as "how crowded is the semantic neighbourhood": a
        well-established clause phrasing lives near many siblings;
        a unique phrasing does not.

    nearest
        Similarity of the single closest neighbour. Bounded in [0, 1] after
        the pseudo-self (exact-duplicate) has been filtered out.

    level
        Five-bucket categorical label derived from `score`, for display only.

    score
        Weighted blend of `density` and `nearest` in [0, 1]. Single scalar
        used for ranking and thresholding.
    """

    density: float
    nearest: float
    score: float
    level: IndexLevel
    k: int  # size of the top-K window used for density
    sim_threshold: float  # similarity cutoff used for density


@dataclass
class QueryResult:
    """Full payload for a single query, shipped to the UI as precomputed JSON."""

    query_clause: Clause
    index: IndexScore
    top_neighbours: list[SimilarClause] = field(default_factory=list)
    similarity_distribution: list[float] = field(default_factory=list)
