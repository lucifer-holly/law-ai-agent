"""Legal Clause Index — a Law Insider-style market alignment score.

Top-level re-exports for convenient importing.
"""

from legal_index.retriever import ClauseRetriever
from legal_index.scorer import compute_index_score, score_clause_by_id
from legal_index.types import Clause, IndexLevel, IndexScore, QueryResult, SimilarClause

__all__ = [
    "Clause",
    "ClauseRetriever",
    "IndexLevel",
    "IndexScore",
    "QueryResult",
    "SimilarClause",
    "compute_index_score",
    "score_clause_by_id",
]

__version__ = "0.1.0"
