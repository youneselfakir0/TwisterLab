import importlib.util
import os

import pytest


def load_get_grafana_password():
    spec = importlib.util.spec_from_file_location(
        "import_dashboard_to_grafana", "scripts/import_dashboard_to_grafana.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.get_grafana_password


def test_get_grafana_password_raises_if_missing(monkeypatch, tmp_path):
    # Ensure the environment variable is not set
    monkeypatch.delenv("GRAFANA_ADMIN_PASSWORD", raising=False)

    # Ensure the /run/secrets file does not exist
    secret_path = "/run/secrets/grafana_admin_password"
    if os.path.exists(secret_path):
        os.remove(secret_path)

    get_grafana_password = load_get_grafana_password()
    with pytest.raises(RuntimeError):
        get_grafana_password()
