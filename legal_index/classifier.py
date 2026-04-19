"""Clause type classification — a placeholder / integration seam.

In this demo corpus every clause arrives with its category label already
attached (that's what CUAD provides). The scorer therefore takes the label
as ground truth and pre-filters retrieval by category.

In a production deployment the classifier would be a discriminative model
(BERT fine-tune, logistic regression over embeddings, etc.) returning
`{"type": "...", "confidence": 0.xx}`. That's the only change required;
the retriever already accepts a `category` filter, and the scorer runs
unchanged.

This stub documents the integration seam without inventing a model we
don't need.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationResult:
    clause_type: str
    confidence: float


class LabelLookupClassifier:
    """Returns the ground-truth label. Used while the demo runs on CUAD.

    Kept here so downstream code can depend on a `Classifier` protocol
    without special-casing the "we already know the label" shortcut.
    """

    def __init__(self, labels_by_clause_id: dict[str, str]):
        self._labels = labels_by_clause_id

    def classify(self, clause_id: str) -> ClassificationResult:
        label = self._labels.get(clause_id)
        if label is None:
            raise KeyError(f"No known label for clause_id={clause_id!r}")
        return ClassificationResult(clause_type=label, confidence=1.0)
