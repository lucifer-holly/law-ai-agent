"""
02 — Build clause embeddings.

This script supports two back-ends:

  --model bge-m3   (default, production quality, ~2GB download, requires internet)
                   Uses BAAI/bge-m3 via sentence-transformers. 1024-dim, multilingual,
                   state-of-the-art for general semantic retrieval.

  --model tfidf    (fallback, ~1MB, zero downloads, fully deterministic)
                   Character 3-5 gram TF-IDF with cosine-like L2-normalised vectors.
                   Used to generate the portable demo bundle that ships with the
                   repo so GitHub viewers see a working Index Score UI immediately.

Both back-ends write:
  data/embeddings/clauses.npy        float32, shape (N, dim), L2-normalised
  data/embeddings/metadata.json      list of clause_id strings in the same order
  data/embeddings/config.json        back-end name + parameters + git-hashable
                                     fingerprint, so downstream scripts can verify

Usage:
  python scripts/02_build_embeddings.py --model tfidf      # for demo / CI
  python scripts/02_build_embeddings.py --model bge-m3     # for real evaluation
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd


def l2_normalize(matrix: np.ndarray) -> np.ndarray:
    """Row-wise L2 normalise so cosine similarity collapses to dot product."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (matrix / norms).astype(np.float32)


def embed_tfidf(texts: list[str]) -> tuple[np.ndarray, dict]:
    """Character 3-5 gram TF-IDF, L2 normalised, dense float32 output.

    Character n-grams are a deliberately domain-appropriate choice for legal text:
    they capture stem-sharing across closely related phrasings
    ('liability', 'liabilities') without an explicit stemmer, and they survive
    punctuation / casing noise common in contract scans.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer

    vec = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
        max_features=8192,
    )
    sparse = vec.fit_transform(texts)
    dense = sparse.toarray().astype(np.float32)
    dense = l2_normalize(dense)
    config = {
        "backend": "tfidf",
        "analyzer": "char_wb",
        "ngram_range": [3, 5],
        "max_features": 8192,
        "dim": int(dense.shape[1]),
        "vocab_size": len(vec.vocabulary_),
    }
    return dense, config


def embed_bge_m3(texts: list[str]) -> tuple[np.ndarray, dict]:
    """BAAI/bge-m3 via sentence-transformers. Requires a one-time ~2GB download."""
    try:
        import torch
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print(
            "ERROR: bge-m3 backend requires 'sentence-transformers' and 'torch'.\n"
            "       Install with:  pip install sentence-transformers torch",
            file=sys.stderr,
        )
        raise

    device = (
        "mps" if torch.backends.mps.is_available()
        else "cuda" if torch.cuda.is_available()
        else "cpu"
    )
    print(f"  device: {device}")
    print("  loading BAAI/bge-m3 ...")
    model = SentenceTransformer("BAAI/bge-m3", device=device)
    print(f"  encoding {len(texts)} clauses ...")
    t0 = time.time()
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
        batch_size=16,
        convert_to_numpy=True,
    ).astype(np.float32)
    print(f"  done in {time.time() - t0:.1f}s")

    config = {
        "backend": "bge-m3",
        "model": "BAAI/bge-m3",
        "dim": int(embeddings.shape[1]),
        "normalized": True,
        "device": device,
    }
    return embeddings, config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default="data/processed/clauses.csv",
        help="Output of scripts/01_prepare_data.py",
    )
    parser.add_argument(
        "--out-dir",
        default="data/embeddings",
    )
    parser.add_argument(
        "--model",
        choices=["tfidf", "bge-m3"],
        default="tfidf",
        help="Embedding backend (default: tfidf for portability)",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"ERROR: {in_path} not found. Run scripts/01_prepare_data.py first.", file=sys.stderr)
        return 1

    df = pd.read_csv(in_path)
    print(f"Loaded {len(df)} clauses from {in_path}")

    texts = df["text"].tolist()
    clause_ids = df["clause_id"].tolist()

    print(f"Backend: {args.model}")
    if args.model == "tfidf":
        embeddings, config = embed_tfidf(texts)
    else:
        embeddings, config = embed_bge_m3(texts)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    np.save(out_dir / "clauses.npy", embeddings)
    with open(out_dir / "metadata.json", "w") as f:
        json.dump({"clause_ids": clause_ids}, f, indent=2)
    with open(out_dir / "config.json", "w") as f:
        json.dump(config, f, indent=2)

    print(f"\nWrote:")
    print(f"  {out_dir / 'clauses.npy'}   shape={embeddings.shape}  dtype={embeddings.dtype}")
    print(f"  {out_dir / 'metadata.json'} {len(clause_ids)} ids")
    print(f"  {out_dir / 'config.json'}   {json.dumps(config)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
