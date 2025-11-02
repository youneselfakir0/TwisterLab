#!/usr/bin/env python3
"""
Test TwisterLang Sync Module
"""

from twisterlang_sync import get_sync_manager, sync_vocabularies
import json
import time


def test_sync_manager():
    """Test the synchronization manager"""
    print("Testing TwisterLang Sync Manager")
    print("=" * 50)

    sync_mgr = get_sync_manager()

    # Test 1: Get metadata
    print("1. Testing vocabulary metadata...")
    meta = sync_mgr.get_vocab_metadata()
    print(f"   Metadata: {json.dumps(meta, indent=2)[:200]}...")

    # Test 2: Get sync status
    print("\n2. Testing sync status...")
    status = sync_mgr.get_sync_status()
    print(f"   Statistics: {status['sync_statistics']}")

    # Test 3: Compare vocabularies
    print("\n3. Testing vocabulary comparison...")
    remote_meta = meta.copy()
    remote_meta['last_update'] = meta['last_update'] - 3600  # 1 hour older
    comparison = sync_mgr.compare_vocabularies(remote_meta)
    print(f"   Comparison: {comparison}")

    # Test 4: Simulate sync across agents
    print("\n4. Testing multi-agent sync simulation...")
    agents = ['agent-1', 'agent-2', 'agent-3']
    sync_results = sync_vocabularies(agents)
    print(f"   Sync results for {len(agents)} agents: "
          f"{len(sync_results['sync_results'])} results")

    # Test 5: Push simulation
    print("\n5. Testing push simulation...")
    push_result = sync_mgr.push_vocabulary('test-agent')
    print(f"   Push result: {push_result['success']}")
    print(f"   Message: {push_result['message']}")

    # Test 6: Pull simulation
    print("\n6. Testing pull simulation...")
    # Create mock remote vocab data
    mock_remote_vocab = {
        'version': '1.1',
        'last_updated': int(time.time()),
        'vocabulary': {
            'test_entry': {
                'code': 'TEST_001',
                'category': 'test',
                'priority': 'low',
                'first_seen': int(time.time())
            }
        }
    }

    pull_result = sync_mgr.pull_vocabulary('test-agent', mock_remote_vocab)
    print(f"   Pull result: {pull_result['success']}")
    print(f"   Message: {pull_result['message']}")

    print("\n✅ All sync manager tests completed successfully!")


if __name__ == "__main__":
    test_sync_manager()