from agents.real.real_backup_agent import RealBackupAgent
import tempfile, asyncio
agent = RealBackupAgent(backup_dir=tempfile.mkdtemp(prefix='test_backups_'))
res = asyncio.run(agent.execute({'operation':'create_backup','backup_type':'full'}))
print('Result:',res)
from pathlib import Path
bd = Path(agent.backup_dir)
for p in sorted(bd.rglob('*')):
    print(p)
print('backup_stats', agent.get_backup_stats())
