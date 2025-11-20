from unittest.mock import MagicMock, AsyncMock
from agents.core.monitoring_agent import MonitoringAgent
from agents.core.backup_agent import BackupAgent
from agents.core.sync_agent import SyncAgent

side_effects = [
    {"status": "critical_failure", "issues": {"database_corruption": True}},
    {"status": "critical_failure", "issues": {"database_corruption": True}},
    {"integrity_status": "compromised", "issues_found": 3},
    {"status": "restored", "components": ["database", "config"]},
    {"consistency_status": "inconsistent", "inconsistencies_found": 2},
    {"reconciled_items": 2, "status": "consistent"},
    {"status": "healthy", "all_systems": "operational"},
]

mock_router = MagicMock()
mock_router.route_to_mcp = AsyncMock(side_effect=side_effects)

mon = MonitoringAgent()
mon.mcp_router = mock_router
backup = BackupAgent()
backup.mcp_router = mock_router
sync = SyncAgent()
sync.mcp_router = mock_router

import asyncio

diag = asyncio.get_event_loop().run_until_complete(mon.execute({'operation': 'diagnostic', 'check_type': 'system'}))
print('DIAG:', diag)
intg = asyncio.get_event_loop().run_until_complete(backup.execute({'operation':'integrity_check'}))
print('BACKUP_INTEGRITY:', intg)
recov = asyncio.get_event_loop().run_until_complete(backup.execute({'operation':'recovery', 'recovery_type':'full'}))
print('BACKUP_RECOVERY:', recov)
recon = asyncio.get_event_loop().run_until_complete(sync.execute({'operation':'reconciliation'}))
print('SYNC_RECON:', recon)
finalh = asyncio.get_event_loop().run_until_complete(mon.execute({'operation':'health_check'}))
print('FINAL', finalh)
print('FINAL result keys', list(finalh.get('result', {}).keys()))
print('FINAL results', finalh.get('result'))
