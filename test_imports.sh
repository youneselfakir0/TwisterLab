#!/bin/bash
echo "=== Testing Python imports ==="
cd /app
python3 -c "import sys; print('Python path:'); [print(p) for p in sys.path]"
echo ""
echo "=== Testing agents.real import ==="
python3 -c "try:
    from agents.real import *
    print('agents.real import: SUCCESS')
except ImportError as e:
    print(f'agents.real import: FAILED - {e}')
except Exception as e:
    print(f'agents.real import: ERROR - {e}')"
echo ""
echo "=== Testing orchestrator import ==="
python3 -c "try:
    from agents.orchestrator.autonomous_orchestrator import AutonomousAgentOrchestrator
    print('orchestrator import: SUCCESS')
except ImportError as e:
    print(f'orchestrator import: FAILED - {e}')
except Exception as e:
    print(f'orchestrator import: ERROR - {e}')"
echo ""
echo "=== Testing metrics import ==="
python3 -c "try:
    from agents.metrics import ollama_requests_total
    print('metrics import: SUCCESS')
except ImportError as e:
    print(f'metrics import: FAILED - {e}')
except Exception as e:
    print(f'metrics import: ERROR - {e}')"
echo ""
echo "=== Testing API app import ==="
python3 -c "try:
    from api_main_corrected import app
    print('API app import: SUCCESS')
except ImportError as e:
    print(f'API app import: FAILED - {e}')
except Exception as e:
    print(f'API app import: ERROR - {e}')"