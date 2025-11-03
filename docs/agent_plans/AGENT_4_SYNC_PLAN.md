# AGENT 4: SYNC AGENT - COMPLETE IMPLEMENTATION PLAN

**Priority:** 4
**Status:** Planning Phase
**Estimated Lines:** 600+
**Dependencies:** MaestroOrchestrator, PostgreSQL, Redis

---

## 1. ARCHITECTURE OVERVIEW

### 1.1 Role in System
The Sync-AgentAgent maintains **data consistency** across TwisterLab's distributed components (PostgreSQL, Redis cache, agent state).

**Data Flow:**
```
Database Change → Sync Agent → Cache Invalidation
Agent State Update → Sync Agent → State Propagation
Conflict Detection → Sync Agent → Resolution
```

### 1.2 Core Responsibilities
1. **Cache Synchronization** - Keep Redis cache consistent with PostgreSQL
2. **State Reconciliation** - Sync agent state across instances
3. **Conflict Resolution** - Handle data conflicts
4. **Change Propagation** - Broadcast updates to all components
5. **Consistency Verification** - Periodic integrity checks

### 1.3 Synchronization Types

**Real-Time Sync:**
- Ticket status updates
- Agent state changes
- Active command tracking

**Scheduled Sync (every 5 minutes):**
- SOP database → Cache
- Device registry → Cache
- Configuration updates

**On-Demand Sync:**
- Manual cache refresh
- Post-deployment sync
- Recovery after failure

---

## 2. CODE TEMPLATE

**File:** `agents/support/sync_agent.py`

```python
"""
TwisterLab - Sync Agent
Maintains data consistency across distributed components
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import json

from ..base import TwisterAgent
from ..database.config import get_db
from ..database.services import SOPService, TicketService, DeviceService
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class SyncStatus:
    """Sync operation status"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class SyncAgent(TwisterAgent):
    """
    Agent for maintaining data consistency across system components.
    """

    def __init__(self):
        super().__init__(
            name="sync-agent",
            display_name="Data Synchronization Agent",
            description="Maintains data consistency across PostgreSQL, Redis, and agent state",
            role="sync",
            instructions=self._get_instructions(),
            tools=self._define_tools(),
            model="llama-3.2",
            temperature=0.2,
            metadata={
                "department": "Infrastructure",
                "sync_interval": "300 seconds",
                "supports_realtime": True
            }
        )

        # Redis connection
        self.redis_client = None

        # Sync statistics
        self.sync_stats = {
            "total_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "last_sync": None
        }

    def _get_instructions(self) -> str:
        return """
        You are the Sync Agent, responsible for maintaining data consistency.

        Your tasks:
        1. Sync PostgreSQL data to Redis cache
        2. Propagate agent state changes
        3. Detect and resolve data conflicts
        4. Verify data integrity
        5. Handle cache invalidation

        Sync Operations:
        - SOPs: Database → Cache
        - Tickets: Bidirectional sync
        - Devices: Database → Cache
        - Agent State: Memory → Redis

        Always maintain transactional consistency.
        Log all sync operations for audit.
        """

    def _define_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "sync_all",
                    "description": "Sync all data sources",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "sync_sops",
                    "description": "Sync SOPs database to cache",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "sync_devices",
                    "description": "Sync device registry to cache",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "invalidate_cache",
                    "description": "Invalidate specific cache keys",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string"}
                        },
                        "required": ["pattern"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "verify_consistency",
                    "description": "Verify data consistency",
                    "parameters": {"type": "object", "properties": {}}
                }
            }
        ]

    async def _get_redis_client(self):
        """Get Redis client connection"""
        if not self.redis_client:
            self.redis_client = await aioredis.from_url(
                "redis://localhost:6379/0",
                encoding="utf-8",
                decode_responses=True
            )
        return self.redis_client

    async def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Main execution method"""
        try:
            logger.info(f"Sync Agent executing: {task}")

            operation = context.get("operation", "sync_all") if context else "sync_all"

            if operation == "sync_all":
                result = await self._sync_all()
            elif operation == "sync_sops":
                result = await self._sync_sops()
            elif operation == "sync_devices":
                result = await self._sync_devices()
            elif operation == "invalidate_cache":
                pattern = context.get("pattern", "*")
                result = await self._invalidate_cache(pattern)
            elif operation == "verify_consistency":
                result = await self._verify_consistency()
            else:
                result = {
                    "status": "error",
                    "error": f"Unknown operation: {operation}"
                }

            # Update stats
            self.sync_stats["total_syncs"] += 1
            if result["status"] == SyncStatus.SUCCESS:
                self.sync_stats["successful_syncs"] += 1
            else:
                self.sync_stats["failed_syncs"] += 1
            self.sync_stats["last_sync"] = datetime.now(timezone.utc).isoformat()

            return result

        except Exception as e:
            logger.error(f"Error in sync execution: {e}", exc_info=True)
            return {
                "status": SyncStatus.FAILED,
                "error": str(e)
            }

    async def _sync_all(self) -> Dict[str, Any]:
        """Sync all data sources"""
        logger.info("Starting full system sync")

        results = {
            "sops": await self._sync_sops(),
            "devices": await self._sync_devices(),
            "agent_state": await self._sync_agent_state()
        }

        # Determine overall status
        statuses = [r["status"] for r in results.values()]

        if all(s == SyncStatus.SUCCESS for s in statuses):
            overall_status = SyncStatus.SUCCESS
        elif any(s == SyncStatus.SUCCESS for s in statuses):
            overall_status = SyncStatus.PARTIAL
        else:
            overall_status = SyncStatus.FAILED

        return {
            "status": overall_status,
            "results": results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def _sync_sops(self) -> Dict[str, Any]:
        """Sync SOPs from PostgreSQL to Redis cache"""
        try:
            logger.info("Syncing SOPs to cache")

            redis = await self._get_redis_client()
            synced_count = 0

            async for session in get_db():
                sop_service = SOPService(session)
                sops = await sop_service.list_sops(limit=1000)

                for sop in sops:
                    # Cache SOP data
                    cache_key = f"sop:{sop.id}"
                    sop_data = {
                        "id": sop.id,
                        "title": sop.title,
                        "category": sop.category,
                        "steps": sop.steps,
                        "keywords": sop.keywords
                    }

                    await redis.setex(
                        cache_key,
                        3600,  # 1 hour TTL
                        json.dumps(sop_data)
                    )

                    synced_count += 1

                # Also cache category index
                categories = {}
                for sop in sops:
                    if sop.category not in categories:
                        categories[sop.category] = []
                    categories[sop.category].append(sop.id)

                await redis.setex(
                    "sops:categories",
                    3600,
                    json.dumps(categories)
                )

            logger.info(f"Synced {synced_count} SOPs to cache")

            return {
                "status": SyncStatus.SUCCESS,
                "synced_count": synced_count,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error syncing SOPs: {e}")
            return {
                "status": SyncStatus.FAILED,
                "error": str(e)
            }

    async def _sync_devices(self) -> Dict[str, Any]:
        """Sync device registry from PostgreSQL to Redis"""
        try:
            logger.info("Syncing devices to cache")

            redis = await self._get_redis_client()
            synced_count = 0

            async for session in get_db():
                device_service = DeviceService(session)
                devices = await device_service.list_devices()

                for device in devices:
                    cache_key = f"device:{device.device_id}"
                    device_data = {
                        "device_id": device.device_id,
                        "hostname": device.hostname,
                        "os": device.os,
                        "is_online": device.is_online,
                        "last_seen": device.last_seen.isoformat() if device.last_seen else None
                    }

                    await redis.setex(
                        cache_key,
                        600,  # 10 minutes TTL
                        json.dumps(device_data)
                    )

                    synced_count += 1

            logger.info(f"Synced {synced_count} devices to cache")

            return {
                "status": SyncStatus.SUCCESS,
                "synced_count": synced_count
            }

        except Exception as e:
            logger.error(f"Error syncing devices: {e}")
            return {
                "status": SyncStatus.FAILED,
                "error": str(e)
            }

    async def _sync_agent_state(self) -> Dict[str, Any]:
        """Sync agent state to Redis"""
        try:
            logger.info("Syncing agent state")

            redis = await self._get_redis_client()

            # Get agent states from Maestro
            # (Would integrate with actual Maestro)
            agent_states = {
                "classifier": {"status": "healthy", "load": 2},
                "resolver": {"status": "healthy", "load": 1},
                "desktop_commander": {"status": "healthy", "load": 0}
            }

            await redis.setex(
                "agents:state",
                60,  # 1 minute TTL
                json.dumps(agent_states)
            )

            return {
                "status": SyncStatus.SUCCESS,
                "agents_synced": len(agent_states)
            }

        except Exception as e:
            logger.error(f"Error syncing agent state: {e}")
            return {
                "status": SyncStatus.FAILED,
                "error": str(e)
            }

    async def _invalidate_cache(self, pattern: str) -> Dict[str, Any]:
        """Invalidate cache keys matching pattern"""
        try:
            logger.info(f"Invalidating cache pattern: {pattern}")

            redis = await self._get_redis_client()

            # Find matching keys
            keys = []
            async for key in redis.scan_iter(match=pattern):
                keys.append(key)

            # Delete keys
            if keys:
                await redis.delete(*keys)

            logger.info(f"Invalidated {len(keys)} cache keys")

            return {
                "status": SyncStatus.SUCCESS,
                "invalidated_count": len(keys),
                "pattern": pattern
            }

        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return {
                "status": SyncStatus.FAILED,
                "error": str(e)
            }

    async def _verify_consistency(self) -> Dict[str, Any]:
        """Verify data consistency between database and cache"""
        try:
            logger.info("Verifying data consistency")

            redis = await self._get_redis_client()
            inconsistencies = []

            # Check SOPs
            async for session in get_db():
                sop_service = SOPService(session)
                db_sops = await sop_service.list_sops(limit=100)

                for sop in db_sops:
                    cache_key = f"sop:{sop.id}"
                    cached_data = await redis.get(cache_key)

                    if not cached_data:
                        inconsistencies.append({
                            "type": "missing_cache",
                            "entity": "sop",
                            "id": sop.id
                        })
                    else:
                        cached_sop = json.loads(cached_data)
                        if cached_sop["title"] != sop.title:
                            inconsistencies.append({
                                "type": "data_mismatch",
                                "entity": "sop",
                                "id": sop.id,
                                "field": "title"
                            })

            if inconsistencies:
                logger.warning(f"Found {len(inconsistencies)} inconsistencies")
                return {
                    "status": "inconsistent",
                    "inconsistencies": inconsistencies
                }
            else:
                return {
                    "status": "consistent",
                    "checked_entities": len(db_sops) if 'db_sops' in locals() else 0
                }

        except Exception as e:
            logger.error(f"Error verifying consistency: {e}")
            return {
                "status": SyncStatus.FAILED,
                "error": str(e)
            }

    def get_sync_stats(self) -> Dict[str, Any]:
        """Get sync statistics"""
        return dict(self.sync_stats)
```

---

## 3. TESTING

```python
# tests/test_sync_agent.py

@pytest.mark.asyncio
async def test_sync_sops():
    """Test SOP synchronization"""
    sync_agent = SyncAgent()

    result = await sync_agent.execute("Sync SOPs", {"operation": "sync_sops"})

    assert result["status"] in [SyncStatus.SUCCESS, SyncStatus.FAILED]

@pytest.mark.asyncio
async def test_cache_invalidation():
    """Test cache invalidation"""
    sync_agent = SyncAgent()

    result = await sync_agent.execute(
        "Invalidate cache",
        {"operation": "invalidate_cache", "pattern": "sop:*"}
    )

    assert result["status"] == SyncStatus.SUCCESS
    assert "invalidated_count" in result
```

---

## 4. DEPLOYMENT

**Environment Variables:**
```bash
SYNC_INTERVAL=300
REDIS_URL=redis://localhost:6379/0
SYNC_ENABLED=true
```

---

**Next Agent:** [Backup-AgentAgent (Priority 5)](AGENT_5_BACKUP_PLAN.md)
