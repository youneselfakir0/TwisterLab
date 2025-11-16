import asyncio
import json

from agents.real.real_monitoring_agent import RealMonitoringAgent


async def main():
    a = RealMonitoringAgent()
    r = await a._check_ports()
    print(json.dumps(r, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
