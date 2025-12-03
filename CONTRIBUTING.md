# Contributing to TwisterLab

Thanks for your interest in contributing to TwisterLab! This document contains a short guide for setting up a development environment, running the test suite, and submitting contributions.

1. Setup
   - Use Python 3.11+ (3.12 is also supported). Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
```

2. Running tests
   - Unit/integration tests:
```powershell
pytest -q
```
   - Run Playwright e2e tests:
```powershell
python -m playwright install --with-deps chromium
pytest -q -m e2e
```

3. Coding standards
   - Formatting and linting is enforced via pre-commit hooks. Run the hooks locally before creating a PR:
```powershell
python -m pip install pre-commit
pre-commit run --all-files
```
   - We also use `ruff`, `isort`, `black` and `mypy` for linting and static checks.

4. Running a local dev server
   - Start the API using uvicorn:
```powershell
uvicorn src.twisterlab.api.main:app --reload --port 8000
```

5. Pydantic / Async DB requirement
   - TwisterLab uses Pydantic v2. Please prefer `.model_dump()` over `.dict()`.
   - The SQL storage implementation expects an async DB engine (e.g., `sqlite+aiosqlite` or an async postgres driver such as `asyncpg`). Update `DATABASE_URL` accordingly in your env.

6. Pull Request Process
   - Fork the repo, create a feature branch, push your changes, and submit a PR against `main`.
   - Add a clear description of the change and tests where applicable.
   - Ensure checks pass (pytest, mypy, ruff, pre-commit) before requesting review.

7. Contact & Support
   - For questions about contribution process or design decisions, open an issue or reach out via the repository maintainers.
