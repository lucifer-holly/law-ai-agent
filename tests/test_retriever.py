"""Unit tests for ClauseRetriever."""

from __future__ import annotations

import numpy as np
import pytest

from legal_index import Clause, ClauseRetriever


def make_retriever(texts_and_types: list[tuple[str, str]], dim: int = 8):
    """Build a retriever over synthetic clauses with orthogonal random vectors."""
    rng = np.random.default_rng(42)
    clauses = [
        Clause(clause_id=f"c_{i:03d}", clause_type=t, contract_name="x.pdf", text=text)
        for i, (text, t) in enumerate(texts_and_types)
    ]
    vecs = rng.standard_normal((len(clauses), dim)).astype(np.float32)
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    return ClauseRetriever(embeddings=vecs, clauses=clauses)


class TestClauseRetriever:
    def test_search_returns_k_results(self):
        r = make_retriever([("foo", "A") for _ in range(20)])
        out = r.search(r.embeddings[0], k=5)
        assert len(out) == 5

    def test_search_results_sorted_by_similarity_desc(self):
        r = make_retriever([("foo", "A") for _ in range(20)])
        out = r.search(r.embeddings[0], k=10)
        sims = [n.similarity for n in out]
        assert sims == sorted(sims, reverse=True)

    def test_self_match_filtered_when_excluded(self):
        r = make_retriever([("foo", "A") for _ in range(20)])
        query = r.embeddings[3]
        out = r.search(query, k=5, exclude_clause_id="c_003")
        assert all(n.clause.clause_id != "c_003" for n in out)

    def test_category_filter_restricts_pool(self):
        items = [("x", "A")] * 10 + [("y", "B")] * 10
        r = make_retriever(items)
        out = r.search(r.embeddings[0], k=20, category="A")
        assert len(out) == 10  # can't exceed the filtered pool
        assert all(n.clause.clause_type == "A" for n in out)

    def test_k_larger_than_pool_is_clamped_not_error(self):
        r = make_retriever([("x", "A")] * 5)
        out = r.search(r.embeddings[0], k=100)
        assert len(out) == 5

    def test_all_similarities_shape_matches_filtered_pool(self):
        items = [("x", "A")] * 10 + [("y", "B")] * 10
        r = make_retriever(items)
        sims = r.all_similarities(r.embeddings[0], category="B")
        assert len(sims) == 10

    def test_invalid_query_shape_raises(self):
        r = make_retriever([("x", "A")] * 5)
        with pytest.raises(ValueError):
            r.search(r.embeddings[:2], k=3)  # 2-D, not 1-D
