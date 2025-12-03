import subprocess
import sys
from typing import Any, List

pytestmark: List[Any] = []


def test_check_pytestmark_duplicates_fixes(tmp_path):
    file = tmp_path / "test_pytestmark_dup.py"
    content = """
pytestmark = pytest.mark.e2e
pytestmark = pytest.mark.slow

def test_sample():
    assert True
"""
    file.write_text(content)
    # Run the script in fix mode
    proc = subprocess.run(
        [sys.executable, "scripts/check_pytestmark_duplicates.py", "--fix", str(file)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    new_content = file.read_text()
    assert "pytestmark = [pytest.mark.e2e, pytest.mark.slow]" in new_content
