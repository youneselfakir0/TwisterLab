# TwisterLab Project

[![Codecov](https://codecov.io/gh/OWNER/REPO/branch/main/graph/badge.svg?token=REPLACE_TOKEN)](https://codecov.io/gh/OWNER/REPO)

TwisterLab is a cloud-native, multi-agent AI infrastructure designed to facilitate complex tasks through autonomous agents. Built on a robust architecture using Python and FastAPI, TwisterLab leverages the Model Context Protocol (MCP) and a custom communication language, TwisterLang, to ensure efficient inter-agent communication and scalability.

## Key Features

- **Autonomous Agents**: A suite of agents that collaborate to perform tasks such as monitoring, backups, and incident resolution.
- **Cloud-Native Architecture**: Fully designed for deployment on Kubernetes, with a focus on CI/CD practices and automation.
- **Structured Communication**: Utilizes TwisterLang for standardized, compressed, and observable communications between agents.
- **Flexible Deployment**: Supports real, hybrid, and mock modes for development and testing, ensuring versatility in various environments.

## Technology Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy v2
- **Database**: PostgreSQL, Redis
- **Orchestration**: Kubernetes (k3s), Docker
- **Monitoring**: Prometheus, Grafana

## Project Structure

- **src/twisterlab/api**: Contains the FastAPI application and its routes.
- **src/twisterlab/agents**: Houses the autonomous agents and their logic.
- **src/twisterlab/twisterlang**: Implements the TwisterLang protocol and its utilities.
- **k8s/**: Contains Kubernetes manifests for deployment and monitoring.
- **docs/**: Documentation for the project and its components.
- **tests/**: Unit tests for various components of the project.
- **scripts/**: Utility scripts for scaffolding and logging.

## Getting Started

To get started with TwisterLab, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd TwisterLab
pip install -r requirements.txt
```

Note: The SQL storage backend uses an async engine (SQLAlchemy Async); when running locally or in CI, set DATABASE_URL to use `sqlite+aiosqlite:///tests.sqlite3` or another async database driver like `postgresql+asyncpg://` for full compatibility.

### Development helpers

Security scan (detect-secrets + gitleaks):
1) Activate venv: `& C:/TwisterLab/venv/Scripts/Activate.ps1`
2) Run the helper: `python scripts/scan_secrets.py`

Web UI (Browser Agent remote control):
1) Start the API server: `python -m uvicorn src.twisterlab.api.main:app --reload --port 8000`
2) Open the UI in your browser: `http://localhost:8000/ui/index.html`

### Running Playwright e2e tests locally

If you'd like to run the Playwright end-to-end UI tests locally:

1. Build and run the API container or start the API with uvicorn (recommended to match CI):

```bash
docker build -t twisterlab-api:latest -f Dockerfile.api .
docker run -d --name twisterlab-api-e2e -p 8000:8000 twisterlab-api:latest
# or run locally:
#   PYTHONPATH=src python -m uvicorn twisterlab.api.main:app --reload --port 8000
```

1. Install test requirements and Playwright browsers (cross-platform):

On Linux/macOS or WSL:

```bash
pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

On Windows PowerShell:

```powershell
python -m pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

1. Run the tests (the E2E tests are only enabled when E2E=1):

On Linux/macOS:

```bash
E2E=1 pytest -q -m e2e
```

On Windows PowerShell:

```powershell
$env:E2E = '1'
pytest -q -m e2e
```

Artifacts (screenshots & traces) will be saved under the `artifacts/` directory when tests fail.


### Running the Application

You can run the FastAPI application locally using:

```bash
python -m uvicorn src.twisterlab.api.main:app --reload --port 8000
```

### Deployment

TwisterLab can be deployed on Kubernetes using the provided manifests in the `k8s/deployments` directory. Ensure that your Kubernetes cluster is set up and configured before deploying.

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.