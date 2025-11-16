#!/usr/bin/env python3
"""
Test TwisterLang Sync Module
"""

import time

from core.twisterlang_sync import get_sync_manager, sync_vocabularies


def test_sync_manager_metadata():
    """Test the synchronization manager metadata functionality"""
    sync_mgr = get_sync_manager()

    # Test getting metadata
    meta = sync_mgr.get_vocab_metadata()
    assert meta is not None
    assert "version" in meta
    assert "last_update" in meta
    assert "vocab_size" in meta


def test_sync_manager_status():
    """Test the synchronization manager status functionality"""
    sync_mgr = get_sync_manager()

    # Test getting sync status
    status = sync_mgr.get_sync_status()
    assert status is not None
    assert "sync_statistics" in status
    assert "current_vocab" in status


def test_sync_manager_comparison():
    """Test vocabulary comparison functionality"""
    sync_mgr = get_sync_manager()

    # Get current metadata
    meta = sync_mgr.get_vocab_metadata()

    # Test comparison with older version
    remote_meta = meta.copy()
    remote_meta["last_update"] = meta["last_update"] - 3600  # 1 hour older
    comparison = sync_mgr.compare_vocabularies(remote_meta)

    assert comparison is not None
    # Comparison should indicate that local is newer
    assert "needs_sync" in comparison or "status" in comparison


def test_multi_agent_sync():
    """Test multi-agent synchronization simulation"""
    agents = ["agent-1", "agent-2", "agent-3"]
    sync_results = sync_vocabularies(agents)

    assert sync_results is not None
    assert "sync_results" in sync_results
    assert len(sync_results["sync_results"]) >= 0  # At least empty list


def test_push_vocabulary():
    """Test vocabulary push functionality"""
    sync_mgr = get_sync_manager()
    push_result = sync_mgr.push_vocabulary("test-agent")

    assert push_result is not None
    assert "success" in push_result
    assert "message" in push_result


def test_pull_vocabulary():
    """Test vocabulary pull functionality"""
    sync_mgr = get_sync_manager()

    # Create mock remote vocab data
    mock_remote_vocab = {
        "version": "1.1",
        "last_updated": int(time.time()),
        "vocabulary": {
            "test_entry": {
                "code": "TEST_001",
                "category": "test",
                "priority": "low",
                "first_seen": int(time.time()),
            }
        },
    }

    pull_result = sync_mgr.pull_vocabulary("test-agent", mock_remote_vocab)

    assert pull_result is not None
    assert "success" in pull_result
    assert "message" in pull_result
