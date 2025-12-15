import sys
from pathlib import Path

# Ensure src/ and repo root are on the import path for tests.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT))
