import asyncio
from agents.real.real_monitoring_agent import RealMonitoringAgent

async def main():
    agent = RealMonitoringAgent()
    res = await agent.execute('Check health', {'operation': 'check_health'})
    import json
    print('Overall:', res['health']['overall'])
    print('Issues:', json.dumps(res['health']['issues'], indent=2))

if __name__ == '__main__':
    asyncio.run(main())
