"""
Security Tests - Secrets Management
Validates that no secrets are hardcoded and all required secrets exist
"""

import re
from pathlib import Path

import pytest


class TestSecretsManagement:
    """Test suite for secrets management"""

    SECRETS_DIR = Path("secrets")
    REQUIRED_SECRETS = [
        "postgres_password.txt",
        "redis_password.txt",
        "admin_password.txt",
        "jwt_secret.txt",
        "webui_secret_key.txt",
        "grafana_admin_password.txt",
    ]

    def test_secrets_directory_exists(self):
        """Secrets directory must exist"""
        assert self.SECRETS_DIR.exists(), "secrets/ directory not found"
        assert self.SECRETS_DIR.is_dir(), "secrets/ is not a directory"

    def test_all_required_secrets_exist(self):
        """All required secret files must exist"""
        for secret in self.REQUIRED_SECRETS:
            secret_path = self.SECRETS_DIR / secret
            assert secret_path.exists(), f"Secret {secret} not found"
            assert secret_path.is_file(), f"{secret} is not a file"

    def test_secrets_not_empty(self):
        """Secret files must not be empty"""
        for secret in self.REQUIRED_SECRETS:
            secret_path = self.SECRETS_DIR / secret
            if secret_path.exists():
                content = secret_path.read_text()
                assert len(content) > 0, f"{secret} is empty"
                assert len(content) >= 16, f"{secret} is too short (<16 chars)"

    def test_secrets_in_gitignore(self):
        """Secrets directory must be in .gitignore"""
        gitignore = Path(".gitignore")
        if gitignore.exists():
            content = gitignore.read_text()
            assert "secrets/" in content, "secrets/ not in .gitignore"

    def test_no_hardcoded_passwords_in_env(self):
        """No hardcoded passwords in .env files"""
        env_files = [
            ".env.prod",
            ".env.production",
            "infrastructure/configs/.env.production.clean",
        ]

        # Patterns to detect hardcoded passwords
        password_patterns = [
            r'PASSWORD=["\']?.+["\']?$',  # PASSWORD=xxx
            r'SECRET=["\']?[A-Za-z0-9]{20,}["\']?$',  # Long secret strings
        ]

        for env_file in env_files:
            path = Path(env_file)
            if not path.exists():
                continue

            content = path.read_text()
            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                # Skip comments and _FILE references (these are OK)
                if line.strip().startswith("#") or "_FILE=" in line:
                    continue

                for pattern in password_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match and "_FILE" not in line:
                        pytest.fail(
                            f"Potential hardcoded password in {env_file}:{i}\n"
                            f"Line: {line.strip()}\n"
                            f"Use _FILE variable instead"
                        )

    def test_no_hardcoded_secrets_in_code(self):
        """No hardcoded secrets in Python code"""
        code_dirs = ["agents", "api", "tests"]

        secret_patterns = [
            r'password\s*=\s*["\'][^"\']{8,}["\']',
            r'secret\s*=\s*["\'][^"\']{16,}["\']',
            r'token\s*=\s*["\'][^"\']{20,}["\']',
        ]

        for code_dir in code_dirs:
            dir_path = Path(code_dir)
            if not dir_path.exists():
                continue

            for py_file in dir_path.rglob("*.py"):
                # Skip test files and init files
                if "test_" in py_file.name or py_file.name == "__init__.py":
                    continue

                # Open files as UTF-8 and ignore decode errors to be robust across editors
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    # Skip comments
                    if line.strip().startswith("#"):
                        continue

                    for pattern in secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Allow test fixtures and examples
                            if "example" in line.lower() or "test" in line.lower():
                                continue
                            pytest.fail(
                                f"Potential hardcoded secret in {py_file}:{i}\n"
                                f"Line: {line.strip()}"
                            )

    def test_secrets_have_minimum_entropy(self):
        """Secrets should have sufficient entropy (not predictable)"""
        for secret in self.REQUIRED_SECRETS:
            secret_path = self.SECRETS_DIR / secret
            if not secret_path.exists():
                continue

            content = secret_path.read_text()

            # Check for common weak patterns
            weak_patterns = [
                "password",
                "123456",
                "admin",
                "secret",
                "changeme",
            ]

            content_lower = content.lower()
            for weak in weak_patterns:
                assert weak not in content_lower, (
                    f"{secret} contains weak pattern: {weak}"
                )

            # Check for repeated characters (aaa, 111, etc.)
            assert not re.search(r"(.)\1{4,}", content), (
                f"{secret} has too many repeated characters"
            )

    def test_docker_compose_uses_secrets(self):
        """docker-compose.prod.yml must define secrets"""
        docker_compose = Path("docker-compose.prod.yml")
        if not docker_compose.exists():
            pytest.skip("docker-compose.prod.yml not found")

        content = docker_compose.read_text()

        # Must have secrets section
        assert "secrets:" in content, "No secrets: section in docker-compose"

        # Must reference all required secrets
        for secret in self.REQUIRED_SECRETS:
            secret_name = secret.replace(".txt", "")
            assert secret_name in content, f"Secret {secret_name} not in docker-compose"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
