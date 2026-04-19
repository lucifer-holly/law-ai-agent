"""
01 — Prepare CUAD clause corpus.

Parses CUAD v1's master_clauses.csv, extracts 6 high-signal clause categories,
samples up to N clauses per category, and writes a clean flat CSV.

Input:  data/raw/master_clauses.csv (downloaded from Zenodo; see README)
Output: data/processed/clauses.csv
        Columns: clause_id, clause_type, contract_name, text, char_len

Usage:  python scripts/01_prepare_data.py --per-category 70
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import sys
from pathlib import Path

import pandas as pd

# The six categories selected for the portfolio demo. See docs/methodology.md
# for the selection rationale (story value + data volume + visual diversity).
SELECTED_CATEGORIES = [
    "Cap On Liability",
    "Anti-Assignment",
    "Governing Law",
    "Termination For Convenience",
    "Change Of Control",
    "Non-Compete",
]

# A short code per category — used in clause_id for human-readable URLs later.
CATEGORY_CODE = {
    "Cap On Liability": "cap",
    "Anti-Assignment": "asn",
    "Governing Law": "law",
    "Termination For Convenience": "tfc",
    "Change Of Control": "coc",
    "Non-Compete": "ncp",
}

# Drop clauses whose raw text falls outside a reasonable legal-sentence range.
MIN_LEN = 60
MAX_LEN = 1500


def parse_clause_list(raw: object) -> list[str]:
    """CUAD stores per-category clause text as a stringified Python list.
    Defensive: handle NaN / malformed strings silently."""
    if pd.isna(raw) or not isinstance(raw, str):
        return []
    try:
        parsed = ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        return []
    if not isinstance(parsed, list):
        return []
    return [s.strip() for s in parsed if isinstance(s, str) and s.strip()]


def short_hash(text: str, n: int = 6) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:n]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default="data/raw/master_clauses.csv",
        help="Path to CUAD master_clauses.csv",
    )
    parser.add_argument(
        "--output",
        default="data/processed/clauses.csv",
        help="Where to write the cleaned flat CSV",
    )
    parser.add_argument(
        "--per-category",
        type=int,
        default=70,
        help="Max clauses sampled per category (default: 70)",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"ERROR: input file not found: {in_path}", file=sys.stderr)
        print("       Download CUAD_v1.zip from https://zenodo.org/records/4595826", file=sys.stderr)
        print("       and place master_clauses.csv under data/raw/", file=sys.stderr)
        return 1

    print(f"Reading {in_path} ...")
    df = pd.read_csv(in_path)
    print(f"  {len(df)} contracts, {len(df.columns)} columns")

    rows: list[dict] = []
    for category in SELECTED_CATEGORIES:
        if category not in df.columns:
            print(f"  WARN: column '{category}' missing from CSV", file=sys.stderr)
            continue
        all_clauses: list[tuple[str, str]] = []  # (contract_name, clause_text)
        for _, row in df[["Filename", category]].iterrows():
            for clause_text in parse_clause_list(row[category]):
                if MIN_LEN <= len(clause_text) <= MAX_LEN:
                    all_clauses.append((row["Filename"], clause_text))

        raw_count = len(all_clauses)
        if raw_count == 0:
            print(f"  WARN: zero usable clauses for '{category}'", file=sys.stderr)
            continue

        tmp = pd.DataFrame(all_clauses, columns=["contract_name", "text"])
        sampled = tmp.sample(
            n=min(args.per_category, raw_count),
            random_state=args.seed,
        ).reset_index(drop=True)

        for i, r in sampled.iterrows():
            rows.append(
                {
                    "clause_id": f"{CATEGORY_CODE[category]}_{i:03d}_{short_hash(r['text'])}",
                    "clause_type": category,
                    "contract_name": r["contract_name"],
                    "text": r["text"],
                    "char_len": len(r["text"]),
                }
            )

        print(f"  {category}: {len(sampled)} sampled / {raw_count} available")

    out_df = pd.DataFrame(rows)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)

    print(f"\nWrote {len(out_df)} clauses -> {out_path}")
    print("\nPer-category summary:")
    print(out_df.groupby("clause_type").agg(n=("clause_id", "count"),
                                             avg_len=("char_len", "mean")).round(0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
