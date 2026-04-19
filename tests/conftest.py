"""Ensure the repo root is on sys.path so `import legal_index` works
when pytest is run from anywhere inside the repo."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
