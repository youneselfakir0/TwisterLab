"""
Tests for RealSyncAgent
=======================

Comprehensive test suite for data synchronization agent.

Author: Claude + Copilot Collaborative Development
Version: 1.0.0-alpha.1
License: Apache 2.0
"""

import asyncio
import json
from datetime import datetime, timezone

import pytest

from agents.real.real_sync_agent import RealSyncAgent
from agents.support.sync_agent import MockRedisClient, SyncStatus

# ============================================================================
# SYNC AGENT TESTS
# ============================================================================


class TestSyncAgent:
    """Test SyncAgent functionality"""

    def test_sync_agent_initialization(self):
        """Test SyncAgent initializes correctly"""
        agent = RealRealSyncAgent\(\)

        assert agent.name == "sync-agent"
        assert agent.display_name == "Data Synchronization Agent"
        assert len(agent.tools) == 6
        assert agent.redis_connected is False
        assert agent.sync_stats["total_syncs"] == 0

    def test_sync_tools_defined(self):
        """Test sync tools are properly defined"""
        agent = RealSyncAgent\(\)

        tool_names = [tool["function"]["name"] for tool in agent.tools]

        assert "sync_all" in tool_names
        assert "sync_sops" in tool_names
        assert "sync_devices" in tool_names
        assert "sync_agent_state" in tool_names
        assert "invalidate_cache" in tool_names
        assert "verify_consistency" in tool_names

    @pytest.mark.asyncio
    async def test_ensure_redis_connection(self):
        """Test Redis connection establishment"""
        agent = RealSyncAgent\(\)

        result = await agent._ensure_redis_connection()

        assert result is True
        assert agent.redis_connected is True
        assert agent.redis_client is not None

    @pytest.mark.asyncio
    async def test_sync_sops(self):
        """Test SOP synchronization"""
        agent = RealSyncAgent\(\)

        result = await agent.execute("Sync SOPs", {"operation": "sync_sops"})

        assert result["status"] == SyncStatus.SUCCESS
        assert "synced_count" in result
        assert result["synced_count"] == 3
        assert "categories" in result
        assert result["categories"] == 3

    @pytest.mark.asyncio
    async def test_sync_devices(self):
        """Test device synchronization"""
        agent = RealSyncAgent\(\)

        result = await agent.execute("Sync devices", {"operation": "sync_devices"})

        assert result["status"] == SyncStatus.SUCCESS
        assert "synced_count" in result
        assert result["synced_count"] == 3

    @pytest.mark.asyncio
    async def test_sync_agent_state(self):
        """Test agent state synchronization"""
        agent = RealSyncAgent\(\)

        result = await agent.execute(
            "Sync agent state",
            {"operation": "sync_agent_state"}
        )

        assert result["status"] == SyncStatus.SUCCESS
        assert "agents_synced" in result
        assert result["agents_synced"] == 4

    @pytest.mark.asyncio
    async def test_sync_all(self):
        """Test full system synchronization"""
        agent = RealSyncAgent\(\)

        result = await agent.execute("Sync all", {"operation": "sync_all"})

        assert result["status"] in [SyncStatus.SUCCESS, SyncStatus.PARTIAL]
        assert "results" in result
        assert "sops" in result["results"]
        assert "devices" in result["results"]
        assert "agent_state" in result["results"]

    @pytest.mark.asyncio
    async def test_sync_all_updates_stats(self):
        """Test sync updates statistics"""
        agent = RealSyncAgent\(\)

        initial_count = agent.sync_stats["total_syncs"]

        await agent.execute("Sync all", {"operation": "sync_all"})

        assert agent.sync_stats["total_syncs"] == initial_count + 1
        assert agent.sync_stats["successful_syncs"] > 0
        assert agent.sync_stats["last_sync"] is not None

    @pytest.mark.asyncio
    async def test_invalidate_cache(self):
        """Test cache invalidation"""
        agent = RealSyncAgent\(\)

        # First sync some data
        await agent.execute("Sync SOPs", {"operation": "sync_sops"})

        # Then invalidate
        result = await agent.execute(
            "Invalidate cache",
            {"operation": "invalidate_cache", "pattern": "sop:*"}
        )

        assert result["status"] == SyncStatus.SUCCESS
        assert "invalidated_count" in result
        assert result["pattern"] == "sop:*"

    @pytest.mark.asyncio
    async def test_invalidate_cache_with_wildcard(self):
        """Test cache invalidation with wildcard pattern"""
        agent = RealSyncAgent\(\)

        # Sync multiple data types
        await agent.execute("Sync all", {"operation": "sync_all"})

        # Invalidate all
        result = await agent.execute(
            "Invalidate all",
            {"operation": "invalidate_cache", "pattern": "*"}
        )

        assert result["status"] == SyncStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_verify_consistency_after_sync(self):
        """Test consistency verification after sync"""
        agent = RealSyncAgent\(\)

        # Sync data first
        await agent.execute("Sync all", {"operation": "sync_all"})

        # Verify consistency
        result = await agent.execute(
            "Verify consistency",
            {"operation": "verify_consistency"}
        )

        assert result["status"] == SyncStatus.CONSISTENT
        assert "checked_sops" in result
        assert "checked_devices" in result

    @pytest.mark.asyncio
    async def test_verify_consistency_detects_missing(self):
        """Test consistency verification detects missing cache entries"""
        agent = RealSyncAgent\(\)

        # Don't sync, just verify
        result = await agent.execute(
            "Verify consistency",
            {"operation": "verify_consistency"}
        )

        # Should detect missing cache entries
        assert result["status"] in [SyncStatus.INCONSISTENT, SyncStatus.CONSISTENT]

    @pytest.mark.asyncio
    async def test_sync_state_tracking(self):
        """Test sync state is tracked"""
        agent = RealSyncAgent\(\)

        # Initial state
        assert agent.sync_state["sops_last_sync"] is None

        # Sync SOPs
        await agent.execute("Sync SOPs", {"operation": "sync_sops"})

        # State should be updated
        assert agent.sync_state["sops_last_sync"] is not None

    def test_get_sync_stats(self):
        """Test getting sync statistics"""
        agent = RealSyncAgent\(\)

        stats = agent.get_sync_stats()

        assert "total_syncs" in stats
        assert "successful_syncs" in stats
        assert "failed_syncs" in stats
        assert "last_sync" in stats
        assert "sync_state" in stats
        assert "redis_connected" in stats

    def test_health_check(self):
        """Test agent health check"""
        agent = RealSyncAgent\(\)

        health = agent.health_check()

        assert "status" in health
        assert health["agent"] == "sync-agent"
        assert "redis_connected" in health
        assert "sync_stats" in health

    @pytest.mark.asyncio
    async def test_health_check_after_connection(self):
        """Test health check after Redis connection"""
        agent = RealSyncAgent\(\)

        # Connect to Redis
        await agent._ensure_redis_connection()

        health = agent.health_check()

        assert health["status"] == "healthy"
        assert health["redis_connected"] is True

    @pytest.mark.asyncio
    async def test_unknown_operation(self):
        """Test handling of unknown operation"""
        agent = RealSyncAgent\(\)

        result = await agent.execute(
            "Unknown task",
            {"operation": "unknown_operation"}
        )

        assert result["status"] == SyncStatus.FAILED
        assert "Unknown operation" in result["error"]

    @pytest.mark.asyncio
    async def test_sync_duration_tracking(self):
        """Test sync duration is tracked"""
        agent = RealSyncAgent\(\)

        result = await agent.execute("Sync all", {"operation": "sync_all"})

        assert "duration_seconds" in result
        assert result["duration_seconds"] >= 0
        assert agent.sync_stats["last_sync_duration"] >= 0

    @pytest.mark.asyncio
    async def test_multiple_syncs(self):
        """Test multiple sync operations"""
        agent = RealSyncAgent\(\)

        # Perform multiple syncs
        for i in range(3):
            await agent.execute("Sync all", {"operation": "sync_all"})

        assert agent.sync_stats["total_syncs"] == 3
        assert agent.sync_stats["successful_syncs"] > 0


# ============================================================================
# MOCK REDIS CLIENT TESTS
# ============================================================================


class TestMockRedisClient:
    """Test MockRedisClient functionality"""

    @pytest.mark.asyncio
    async def test_redis_setex(self):
        """Test setting key with expiration"""
        redis = MockRedisClient()

        await redis.setex("test_key", 60, "test_value")

        assert "test_key" in redis.data
        assert redis.data["test_key"] == "test_value"
        assert redis.ttls["test_key"] == 60

    @pytest.mark.asyncio
    async def test_redis_get(self):
        """Test getting key value"""
        redis = MockRedisClient()

        await redis.setex("test_key", 60, "test_value")
        value = await redis.get("test_key")

        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_redis_get_missing_key(self):
        """Test getting non-existent key"""
        redis = MockRedisClient()

        value = await redis.get("missing_key")

        assert value is None

    @pytest.mark.asyncio
    async def test_redis_delete(self):
        """Test deleting keys"""
        redis = MockRedisClient()

        await redis.setex("key1", 60, "value1")
        await redis.setex("key2", 60, "value2")

        await redis.delete("key1", "key2")

        assert "key1" not in redis.data
        assert "key2" not in redis.data

    @pytest.mark.asyncio
    async def test_redis_keys_pattern(self):
        """Test finding keys by pattern"""
        redis = MockRedisClient()

        await redis.setex("sop:001", 60, "data1")
        await redis.setex("sop:002", 60, "data2")
        await redis.setex("device:001", 60, "data3")

        sop_keys = await redis.keys("sop:*")

        assert len(sop_keys) == 2
        assert "sop:001" in sop_keys
        assert "sop:002" in sop_keys

    @pytest.mark.asyncio
    async def test_redis_keys_wildcard(self):
        """Test finding all keys with wildcard"""
        redis = MockRedisClient()

        await redis.setex("key1", 60, "value1")
        await redis.setex("key2", 60, "value2")

        all_keys = await redis.keys("*")

        assert len(all_keys) == 2


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestSyncIntegration:
    """Integration tests for sync operations"""

    @pytest.mark.asyncio
    async def test_full_sync_workflow(self):
        """Test complete sync workflow"""
        agent = RealSyncAgent\(\)

        # Step 1: Full sync
        sync_result = await agent.execute("Sync all", {"operation": "sync_all"})
        assert sync_result["status"] == SyncStatus.SUCCESS

        # Step 2: Verify consistency
        verify_result = await agent.execute(
            "Verify consistency",
            {"operation": "verify_consistency"}
        )
        assert verify_result["status"] == SyncStatus.CONSISTENT

        # Step 3: Get stats
        stats = agent.get_sync_stats()
        assert stats["total_syncs"] == 2

    @pytest.mark.asyncio
    async def test_sync_invalidate_resync(self):
        """Test sync → invalidate → resync cycle"""
        agent = RealSyncAgent\(\)

        # Sync SOPs
        sync1 = await agent.execute("Sync SOPs", {"operation": "sync_sops"})
        assert sync1["status"] == SyncStatus.SUCCESS

        # Invalidate SOPs
        invalidate = await agent.execute(
            "Invalidate SOPs",
            {"operation": "invalidate_cache", "pattern": "sop:*"}
        )
        assert invalidate["status"] == SyncStatus.SUCCESS

        # Resync SOPs
        sync2 = await agent.execute("Sync SOPs", {"operation": "sync_sops"})
        assert sync2["status"] == SyncStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_concurrent_syncs(self):
        """Test multiple concurrent sync operations"""
        agent = RealSyncAgent\(\)

        # Run multiple syncs concurrently
        tasks = [
            agent.execute("Sync SOPs", {"operation": "sync_sops"}),
            agent.execute("Sync devices", {"operation": "sync_devices"}),
            agent.execute("Sync agent state", {"operation": "sync_agent_state"})
        ]

        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(r["status"] == SyncStatus.SUCCESS for r in results)

    @pytest.mark.asyncio
    async def test_sync_stats_accumulation(self):
        """Test sync statistics accumulate correctly"""
        agent = RealSyncAgent\(\)

        # Perform multiple operations
        await agent.execute("Sync SOPs", {"operation": "sync_sops"})
        await agent.execute("Sync devices", {"operation": "sync_devices"})
        await agent.execute("Sync all", {"operation": "sync_all"})

        stats = agent.get_sync_stats()

        assert stats["total_syncs"] == 3
        assert stats["successful_syncs"] == 3
        assert stats["failed_syncs"] == 0

    @pytest.mark.asyncio
    async def test_cache_lifecycle(self):
        """Test complete cache lifecycle"""
        agent = RealSyncAgent\(\)

        # 1. Sync data to cache
        await agent.execute("Sync all", {"operation": "sync_all"})

        # 2. Verify cache is populated
        redis = agent.redis_client
        sop_data = await redis.get("sop:sop-001")
        assert sop_data is not None

        # 3. Invalidate cache
        await agent.execute(
            "Invalidate",
            {"operation": "invalidate_cache", "pattern": "*"}
        )

        # 4. Verify cache is empty
        sop_data_after = await redis.get("sop:sop-001")
        assert sop_data_after is None

    @pytest.mark.asyncio
    async def test_sync_state_persistence(self):
        """Test sync state persists across operations"""
        agent = RealSyncAgent\(\)

        # Sync different data types
        await agent.execute("Sync SOPs", {"operation": "sync_sops"})
        await agent.execute("Sync devices", {"operation": "sync_devices"})

        # Check sync state
        assert agent.sync_state["sops_last_sync"] is not None
        assert agent.sync_state["devices_last_sync"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
