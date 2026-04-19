"""Clause retrieval against a precomputed, L2-normalised embedding matrix.

The retriever is deliberately simple (exact cosine search, O(N) per query) —
this repo never indexes more than a few hundred clauses for demo purposes, and
an HNSW index would add dependency weight without changing any of the insights
the UI communicates. Swapping this for Chroma / Qdrant is a one-class change.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from legal_index.types import Clause, SimilarClause


@dataclass
class ClauseRetriever:
    """Holds the embeddings and the aligned clause records in memory."""

    embeddings: np.ndarray  # shape (N, D), float32, L2-normalised
    clauses: list[Clause]   # length N, index-aligned with `embeddings`

    @classmethod
    def from_files(
        cls,
        clauses_csv: str,
        embeddings_npy: str,
    ) -> "ClauseRetriever":
        df = pd.read_csv(clauses_csv)
        clauses = [
            Clause(
                clause_id=row.clause_id,
                clause_type=row.clause_type,
                contract_name=row.contract_name,
                text=row.text,
            )
            for row in df.itertuples(index=False)
        ]
        embeddings = np.load(embeddings_npy)
        if embeddings.shape[0] != len(clauses):
            raise ValueError(
                f"Embedding count ({embeddings.shape[0]}) != clause count ({len(clauses)})."
            )
        return cls(embeddings=embeddings.astype(np.float32), clauses=clauses)

    def __len__(self) -> int:
        return len(self.clauses)

    def search(
        self,
        query_vec: np.ndarray,
        k: int = 20,
        category: str | None = None,
        exclude_clause_id: str | None = None,
    ) -> list[SimilarClause]:
        """Return the top-k most similar clauses.

        Parameters
        ----------
        query_vec
            Unit-length query embedding, shape (D,).
        k
            Number of neighbours to return (after filtering).
        category
            If given, restrict search to clauses of this category. This is the
            "document-level pre-filter" pattern from Law Insider: classify
            first, then search inside the relevant bucket only.
        exclude_clause_id
            If given, drop this clause_id from results — used when the query
            is itself from the corpus (avoids a trivial self-match at rank 1).
        """
        if query_vec.ndim != 1:
            raise ValueError("query_vec must be 1-D")
        q = query_vec.astype(np.float32)

        sims = self.embeddings @ q  # cosine similarity (both sides L2-normalised)

        mask = np.ones(len(self.clauses), dtype=bool)
        if category is not None:
            mask &= np.array([c.clause_type == category for c in self.clauses])
        if exclude_clause_id is not None:
            mask &= np.array([c.clause_id != exclude_clause_id for c in self.clauses])

        candidate_indices = np.where(mask)[0]
        if len(candidate_indices) == 0:
            return []

        candidate_sims = sims[candidate_indices]
        # argpartition is O(N), sort the top-k only
        top_k = min(k, len(candidate_indices))
        top_partition = np.argpartition(-candidate_sims, top_k - 1)[:top_k]
        top_sorted = top_partition[np.argsort(-candidate_sims[top_partition])]

        results: list[SimilarClause] = []
        for local_idx in top_sorted:
            global_idx = candidate_indices[local_idx]
            results.append(
                SimilarClause(
                    clause=self.clauses[global_idx],
                    similarity=float(candidate_sims[local_idx]),
                )
            )
        return results

    def all_similarities(
        self,
        query_vec: np.ndarray,
        category: str | None = None,
        exclude_clause_id: str | None = None,
    ) -> np.ndarray:
        """Return the full vector of similarities post-filter (for histograms)."""
        sims = self.embeddings @ query_vec.astype(np.float32)
        mask = np.ones(len(self.clauses), dtype=bool)
        if category is not None:
            mask &= np.array([c.clause_type == category for c in self.clauses])
        if exclude_clause_id is not None:
            mask &= np.array([c.clause_id != exclude_clause_id for c in self.clauses])
        return sims[mask]
