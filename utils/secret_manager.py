import os
from typing import Optional


def read_secret_file(secret_name: str, default_value: Optional[str] = None) -> str:
    """
    Reads a secret from a Docker secret file, falling back to an environment variable.
    Raises an error if the secret is not found and no default is provided.
    """
    secret_path = f"/run/secrets/{secret_name}"
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            return f.read().strip()

    env_value = os.getenv(secret_name)
    if env_value:
        return env_value

    if default_value is not None:
        return default_value

    raise ValueError(
        f"Secret '{secret_name}' not found in Docker secrets or environment variables."
    )
