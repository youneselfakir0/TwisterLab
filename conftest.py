import sys
from pathlib import Path

# Ensure 'src' is on sys.path for tests running from repository root (e.g., scaffold dir tests)
ROOT = Path(__file__).resolve().parents[0]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
