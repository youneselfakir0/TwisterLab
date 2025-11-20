import asyncio
import json
import pytest
from typing import Any
from pathlib import Path
from agents.real.real_backup_agent import RealBackupAgent
from agents.metrics import backup_retention_runs_total
async def _get_counter_value(counter: Any) -> float:
    """Return the first sample value from a prometheus counter collect() output.

    If there are no metric families or samples, return 0.0.
    """
    # collect() returns a generator; convert to a list and get the first sample
    metric_families = list(counter.collect())
    if not metric_families:
        return 0.0
    samples = metric_families[0].samples
    if not samples:
        return 0.0
    return float(samples[0].value)
# Duplicate test removed; the real test is defined below.
@pytest.mark.integration
async def test_retention_worker_increments_metric(tmp_path: Path) -> None:
    agent = RealBackupAgent(backup_dir=str(tmp_path))
    initial = await _get_counter_value(backup_retention_runs_total)

    # Create an empty manifest entry and files so the retention path updates the metrics on run
    backup_id = "twisterlab_test_1"
    archive_path = agent._archive_path(backup_id)
    metadata_path = agent._metadata_path(backup_id)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    archive_path.write_text("")
    metadata_path.write_text(json.dumps({"backup_id": backup_id, "timestamp": "2025-11-16T00:00:00Z"}))
    agent._add_to_manifest({"backup_id": backup_id, "timestamp": "2025-11-16T00:00:00Z"})
    # Start retention worker with a short interval
    started = await agent.start_scheduled_retention(1)
    assert started

    # Let it run once or twice
    await asyncio.sleep(1.5)

    # Stop it
    stopped = await agent.stop_scheduled_retention()
    assert stopped

    final = await _get_counter_value(backup_retention_runs_total)
    assert final >= initial + 1
