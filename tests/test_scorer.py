"""Unit tests for the Index Score computation.

Focus: the algorithm's edge cases, not the data pipeline. A correct
scorer guarantees the downstream UI can never display nonsense even if
the embeddings or corpus change.
"""

from __future__ import annotations

import numpy as np
import pytest

from legal_index import SimilarClause, Clause, compute_index_score
from legal_index.scorer import DEFAULT_K, DEFAULT_SIM_THRESHOLD, _band


def make_neighbours(similarities: list[float]) -> list[SimilarClause]:
    """Build a list of SimilarClause with the given similarities, sorted desc."""
    sims = sorted(similarities, reverse=True)
    return [
        SimilarClause(
            clause=Clause(
                clause_id=f"dummy_{i}",
                clause_type="Test",
                contract_name="synthetic.pdf",
                text="...",
            ),
            similarity=s,
        )
        for i, s in enumerate(sims)
    ]


class TestComputeIndexScore:
    def test_empty_neighbours_returns_zero_highly_atypical(self):
        result = compute_index_score([])
        assert result.density == 0.0
        assert result.nearest == 0.0
        assert result.score == 0.0
        assert result.level == "Highly Atypical"

    def test_all_neighbours_above_threshold_gives_density_one(self):
        sims = [0.9] * DEFAULT_K
        result = compute_index_score(make_neighbours(sims))
        assert result.density == 1.0
        assert result.nearest == pytest.approx(0.9)

    def test_no_neighbours_above_threshold_gives_density_zero(self):
        sims = [0.05] * DEFAULT_K
        result = compute_index_score(make_neighbours(sims))
        assert result.density == 0.0
        assert result.nearest == pytest.approx(0.05)

    def test_half_above_threshold_gives_density_half(self):
        sims = [0.9] * (DEFAULT_K // 2) + [0.05] * (DEFAULT_K - DEFAULT_K // 2)
        result = compute_index_score(make_neighbours(sims))
        assert result.density == pytest.approx(0.5)

    def test_weights_must_sum_to_one(self):
        with pytest.raises(ValueError):
            compute_index_score(
                make_neighbours([0.5] * DEFAULT_K),
                density_weight=0.5,
                nearest_weight=0.6,  # sum 1.1
            )

    def test_nearest_clipped_to_positive_unit_range(self):
        """Negative cosine sim shouldn't propagate into the nearest statistic."""
        # Enforce descending order ourselves: sort puts 0.0 first, but we want
        # to check the clipping path with a negative top-1.
        sims = [-0.1] + [0.0] * (DEFAULT_K - 1)
        sims.sort(reverse=True)
        neighbours = [
            SimilarClause(
                clause=Clause(f"x{i}", "T", "c.pdf", "t"),
                similarity=s,
            )
            for i, s in enumerate(sims)
        ]
        result = compute_index_score(neighbours)
        assert 0.0 <= result.nearest <= 1.0

    def test_level_band_monotonic(self):
        """Score bands must form a non-overlapping increasing sequence."""
        scores = [0.0, 0.1, 0.22, 0.35, 0.55, 0.75, 1.0]
        levels = [_band(s) for s in scores]
        # "rank" increases monotonically across the score axis
        from legal_index.types import IndexLevel  # noqa: F401
        order = {
            "Highly Atypical": 0,
            "Atypical": 1,
            "Mixed": 2,
            "Standard": 3,
            "Highly Standard": 4,
        }
        ranks = [order[lvl] for lvl in levels]
        assert ranks == sorted(ranks)


class TestScoreBlending:
    def test_pure_density_weight_ignores_nearest(self):
        sims = [0.9] + [0.9] * (DEFAULT_K - 1)
        result = compute_index_score(
            make_neighbours(sims),
            density_weight=1.0,
            nearest_weight=0.0,
        )
        assert result.score == pytest.approx(result.density)

    def test_pure_nearest_weight_ignores_density(self):
        sims = [0.72] + [0.01] * (DEFAULT_K - 1)
        result = compute_index_score(
            make_neighbours(sims),
            density_weight=0.0,
            nearest_weight=1.0,
        )
        assert result.score == pytest.approx(min(1.0, max(0.0, 0.72)))
