import os
import pytest
import shutil


@pytest.fixture(autouse=True)
def clean_backups_dir(tmp_path, monkeypatch):
    """Autouse fixture to ensure backup_dir is clean between tests.

    Some tests create backups under a temp backup_dir - ensure it's isolated.
    This fixture creates a unique path for `TWISTERLAB_TEST_BACKUP_DIR` and
    sets it in the environment for tests that rely on reading env variable.
    """
    tmp = tmp_path / "test_backups"
    tmp.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("TWISTERLAB_TEST_BACKUP_DIR", str(tmp))
    yield
    # cleanup
    try:
        shutil.rmtree(str(tmp))
    except Exception:
        pass
import os
import pytest


@pytest.fixture(autouse=True)
def ollama_test_mode(request, monkeypatch):
    """
    If the test is marked with 'integration', set OLLAMA_TEST_MODE to 'true'
    so the Ollama client returns deterministic responses instead of hitting
    external Ollama servers during CI.
    """
    if "integration" in request.keywords:
        monkeypatch.setenv("OLLAMA_TEST_MODE", "true")

    # No return; fixture is autouse and only sets environment when needed


def pytest_ignore_collect(path):
    """
    Ignore certain integration CLI-style test scripts which are not intended
    to be collected by pytest as unit tests. These scripts usually perform
    interactive integration/edgeserver checks (API calls to EDGESERVER) and
    should not run during CI unit test runs unless explicitly invoked.
    """
    try:
        p = str(path)
        # Skip known integration CLI scripts located in tests/ that are not pytest-style
        if p.endswith("test_integration_real_agents.py") or p.endswith("test_agent_communication.py"):
            return True
        # Skip any test scripts that define a top-level 'run_integration_tests' function
        # to avoid executing CLI-style scripts accidentally.
        text = path.read_text(encoding='utf-8')
        if "def run_integration_tests(" in text:
            return True
    except Exception:
        # Ignore errors while reading path; do not block test collection
        pass
    return False
