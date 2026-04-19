# References

## Primary references

### CUAD corpus

- Hendrycks, D., Burns, C., Chen, A., & Ball, S. (2021).
  **CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review.**
  NeurIPS 2021 Datasets and Benchmarks Track.
  [arXiv:2103.06268](https://arxiv.org/abs/2103.06268) ·
  [dataset on Zenodo](https://zenodo.org/records/4595826) ·
  [The Atticus Project](https://www.atticusprojectai.org/cuad)

  The data layer of this repo. 510 EDGAR commercial contracts, 41
  clause categories, 13,000+ expert annotations. CC-BY 4.0.

### Law Insider — the architectural inspiration

- [Law Insider](https://www.lawinsider.com/) — commercial
  contract-drafting tooling with the Index Score mechanism this repo
  reverse-engineers at demo scale.
- [Telos Labs project description](https://teloslabs.co/work/law-insider/) —
  public write-up of the collaboration behind Law Insider's AI layer
  (one of the few available sources on the Index Score's actual
  implementation details).

The product uses a much larger proprietary corpus and likely a
fine-tuned legal embedding plus structural-alignment features. The
essential *architectural* claim — that market-alignment scoring can
happen off the LLM path, driven by geometry over embeddings — is what
this repo reproduces.

---

## Embedding model

- **BAAI/bge-m3** — Chen et al., *BGE M3-Embedding: Multi-Lingual,
  Multi-Functionality, Multi-Granularity Text Embeddings through
  Self-Knowledge Distillation* (2024).
  [arXiv:2402.03216](https://arxiv.org/abs/2402.03216) ·
  [HuggingFace](https://huggingface.co/BAAI/bge-m3)

  The strong-embedding option wired up in
  `scripts/02_build_embeddings.py`. 1,024 dimensions, multi-lingual,
  state of the art as of 2024–25 for general-purpose retrieval.

- **TF-IDF (character n-gram, via scikit-learn)** — the portable
  fallback. No model to download, deterministic, demo-friendly.
  Used by default so the shipped demo data can be reproduced with
  `pip install -r requirements.txt` alone.

---

## Background

For an intuition primer on embeddings, retrieval, and the "no LLM on
the critical path" pattern applied here, see:

- Jay Alammar — [The Illustrated Word2vec](https://jalammar.github.io/illustrated-word2vec/)
- Malkov & Yashunin (2018) — *Efficient and robust approximate nearest
  neighbor search using Hierarchical Navigable Small World graphs*
  (the HNSW algorithm underlying most vector DBs, including Chroma).
  [arXiv:1603.09320](https://arxiv.org/abs/1603.09320)
- Gao et al. (2023) — *Retrieval-Augmented Generation for Large
  Language Models: A Survey.*
  [arXiv:2312.10997](https://arxiv.org/abs/2312.10997)
