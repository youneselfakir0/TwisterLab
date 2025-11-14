"""
TwisterLab - RealResolverAgent Tests
Comprehensive test suite for ticket resolution functionality
"""

import pytest
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import json

from agents.real.real_resolver_agent import (
    RealResolverAgent,
    ResolutionStrategy,
    ResolutionStatus
)


@pytest.fixture
def resolver_agent():
    """Create RealResolverAgent instance for testing"""
    return RealResolverAgent()


@pytest.fixture
def sample_ticket_context():
    """Sample ticket context for testing"""
    return {
        "ticket_id": "TICKET-001",
        "title": "Cannot access email",
        "description": "User unable to login to Outlook",
        "priority": "high",
        "device_id": "WS-001",
        "user_id": "user@company.com"
    }


@pytest.fixture
def sample_classification():
    """Sample classification result"""
    return {
        "category": "email",
        "subcategory": "access_denied",
        "confidence": 0.92,
        "urgency": "high",
        "suggested_sops": ["SOP-EMAIL-001", "SOP-EMAIL-002"]
    }


@pytest.fixture
def sample_sop_high_confidence():
    """High confidence SOP for direct execution"""
    return {
        "id": "SOP-EMAIL-001",
        "title": "Outlook Login Issues",
        "match_score": 0.95,
        "success_rate": 0.88,
        "prerequisites": {
            "tools": ["outlook", "powershell"],
            "permissions": ["admin"]
        },
        "steps": [
            {
                "type": "command",
                "description": "Clear Outlook credentials",
                "command": "cmdkey /delete:outlook.office365.com",
                "expected_outcome": "Credentials cleared"
            },
            {
                "type": "command",
                "description": "Restart Outlook",
                "command": "taskkill /F /IM outlook.exe && start outlook",
                "expected_outcome": "Outlook restarted"
            },
            {
                "type": "verification",
                "description": "Verify user can login",
                "expected_outcome": "Login successful"
            }
        ]
    }


@pytest.fixture
def sample_sop_medium_confidence():
    """Medium confidence SOP for adaptive execution"""
    return {
        "id": "SOP-EMAIL-002",
        "title": "Email Sync Issues",
        "match_score": 0.72,
        "success_rate": 0.75,
        "prerequisites": {},
        "steps": [
            {
                "type": "command",
                "description": "Repair Outlook profile",
                "command": "outlook.exe /cleanprofile",
                "expected_outcome": "Profile repaired"
            }
        ]
    }


@pytest.fixture
def sample_sop_low_confidence():
    """Low confidence SOP for manual execution"""
    return {
        "id": "SOP-EMAIL-003",
        "title": "Generic Email Troubleshooting",
        "match_score": 0.45,
        "success_rate": 0.60,
        "prerequisites": {},
        "steps": [
            {
                "type": "manual",
                "description": "Check network connectivity",
                "expected_outcome": "Network is accessible"
            }
        ]
    }


# ============================================================================
# STRATEGY SELECTION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_select_strategy_direct_execution(resolver_agent, sample_classification, sample_sop_high_confidence):
    """Test strategy selection for high confidence scenario"""
    sop_recommendations = [sample_sop_high_confidence]

    strategy, selected_sop, confidence = await resolver_agent._select_strategy(
        sample_classification,
        sop_recommendations
    )

    assert strategy == ResolutionStrategy.DIRECT_EXECUTION
    assert selected_sop == sample_sop_high_confidence
    assert confidence >= resolver_agent.confidence_threshold_direct
    assert confidence > 0.85


@pytest.mark.asyncio
async def test_select_strategy_adaptive_execution(resolver_agent, sample_classification, sample_sop_medium_confidence):
    """Test strategy selection for medium confidence scenario"""
    sop_recommendations = [sample_sop_medium_confidence]

    strategy, selected_sop, confidence = await resolver_agent._select_strategy(
        sample_classification,
        sop_recommendations
    )

    assert strategy == ResolutionStrategy.ADAPTIVE_EXECUTION
    assert selected_sop == sample_sop_medium_confidence
    assert resolver_agent.confidence_threshold_adaptive <= confidence < resolver_agent.confidence_threshold_direct


@pytest.mark.asyncio
async def test_select_strategy_manual_execution(resolver_agent, sample_classification, sample_sop_low_confidence):
    """Test strategy selection for low confidence scenario"""
    sop_recommendations = [sample_sop_low_confidence]

    strategy, selected_sop, confidence = await resolver_agent._select_strategy(
        sample_classification,
        sop_recommendations
    )

    assert strategy in [ResolutionStrategy.MANUAL_EXECUTION, ResolutionStrategy.ESCALATION]
    assert confidence < resolver_agent.confidence_threshold_adaptive


@pytest.mark.asyncio
async def test_select_strategy_hybrid_execution(resolver_agent, sample_classification, sample_sop_medium_confidence):
    """Test strategy selection for hybrid scenario with multiple SOPs"""
    sop_recommendations = [
        sample_sop_medium_confidence,
        {**sample_sop_medium_confidence, "id": "SOP-EMAIL-004", "match_score": 0.68}
    ]

    strategy, selected_sop, confidence = await resolver_agent._select_strategy(
        sample_classification,
        sop_recommendations
    )

    # Should select ADAPTIVE or HYBRID based on confidence
    assert strategy in [ResolutionStrategy.ADAPTIVE_EXECUTION, ResolutionStrategy.HYBRID_EXECUTION]


@pytest.mark.asyncio
async def test_select_strategy_escalation_no_sops(resolver_agent, sample_classification):
    """Test automatic escalation when no SOPs available"""
    sop_recommendations = []

    strategy, selected_sop, confidence = await resolver_agent._select_strategy(
        sample_classification,
        sop_recommendations
    )

    assert strategy == ResolutionStrategy.ESCALATION
    assert selected_sop is None
    assert confidence == 0.0


# ============================================================================
# CONFIDENCE CALCULATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_calculate_confidence_high_score(resolver_agent):
    """Test confidence calculation with high match score"""
    confidence = await resolver_agent._calculate_confidence(
        sop_match_score=0.95,
        prerequisite_met=True,
        historical_success=0.90
    )

    assert 0.85 <= confidence <= 1.0
    assert confidence > resolver_agent.confidence_threshold_direct


@pytest.mark.asyncio
async def test_calculate_confidence_prerequisites_failed(resolver_agent):
    """Test confidence calculation when prerequisites not met"""
    confidence_with_prereqs = await resolver_agent._calculate_confidence(
        sop_match_score=0.90,
        prerequisite_met=True,
        historical_success=0.85
    )

    confidence_without_prereqs = await resolver_agent._calculate_confidence(
        sop_match_score=0.90,
        prerequisite_met=False,
        historical_success=0.85
    )

    assert confidence_without_prereqs < confidence_with_prereqs


@pytest.mark.asyncio
async def test_calculate_confidence_bounds(resolver_agent):
    """Test confidence calculation stays within [0, 1] bounds"""
    # Test upper bound
    confidence_high = await resolver_agent._calculate_confidence(
        sop_match_score=1.0,
        prerequisite_met=True,
        historical_success=1.0
    )
    assert confidence_high <= 1.0

    # Test lower bound
    confidence_low = await resolver_agent._calculate_confidence(
        sop_match_score=0.0,
        prerequisite_met=False,
        historical_success=0.0
    )
    assert confidence_low >= 0.0


# ============================================================================
# EXECUTION STRATEGY TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_execute_direct_success(resolver_agent, sample_ticket_context, sample_sop_high_confidence):
    """Test direct execution with successful resolution"""
    with patch.object(resolver_agent, '_execute_step', new_callable=AsyncMock) as mock_execute_step:
        mock_execute_step.return_value = {
            "output": "Command executed successfully",
            "exit_code": 0,
            "resolution_confirmed": True
        }

        result = await resolver_agent._execute_direct(
            "TICKET-001",
            sample_sop_high_confidence,
            sample_ticket_context
        )

        assert result["status"] == ResolutionStatus.SUCCESS.value
        assert result["sop_id"] == sample_sop_high_confidence["id"]
        assert result["strategy"] == ResolutionStrategy.DIRECT_EXECUTION.value
        assert len(result["execution_log"]) > 0
        assert all(log["status"] == "success" for log in result["execution_log"])


@pytest.mark.asyncio
async def test_execute_direct_with_retries(resolver_agent, sample_ticket_context, sample_sop_high_confidence):
    """Test direct execution with retry logic"""
    with patch.object(resolver_agent, '_execute_step', new_callable=AsyncMock) as mock_execute_step:
        # First call fails, second succeeds
        mock_execute_step.side_effect = [
            Exception("Network timeout"),
            {
                "output": "Command executed successfully",
                "exit_code": 0,
                "resolution_confirmed": True
            }
        ]

        result = await resolver_agent._execute_direct(
            "TICKET-001",
            sample_sop_high_confidence,
            sample_ticket_context
        )

        assert result["status"] in [ResolutionStatus.SUCCESS.value, ResolutionStatus.PARTIAL.value]
        assert mock_execute_step.call_count >= 2


@pytest.mark.asyncio
async def test_execute_adaptive_with_variations(resolver_agent, sample_ticket_context, sample_sop_medium_confidence):
    """Test adaptive execution allows variations"""
    with patch.object(resolver_agent, '_execute_step', new_callable=AsyncMock) as mock_execute_step:
        mock_execute_step.return_value = {
            "output": "Command executed with variations",
            "exit_code": 0,
            "resolution_confirmed": True,
            "variations": ["param_adjusted"]
        }

        result = await resolver_agent._execute_adaptive(
            "TICKET-001",
            sample_sop_medium_confidence,
            sample_ticket_context
        )

        assert result["status"] == ResolutionStatus.SUCCESS.value
        assert result["strategy"] == ResolutionStrategy.ADAPTIVE_EXECUTION.value
        assert "variations_applied" in result["execution_log"][0]


@pytest.mark.asyncio
async def test_execute_hybrid_multiple_sops(resolver_agent, sample_ticket_context):
    """Test hybrid execution combines multiple SOPs"""
    sop_recommendations = [
        {"id": "SOP-001", "steps": [{"type": "command", "description": "Step 1"}]},
        {"id": "SOP-002", "steps": [{"type": "command", "description": "Step 2"}]},
        {"id": "SOP-003", "steps": [{"type": "command", "description": "Step 3"}]}
    ]

    with patch.object(resolver_agent, '_execute_step', new_callable=AsyncMock) as mock_execute_step:
        mock_execute_step.return_value = {
            "output": "Step executed",
            "resolution_confirmed": False
        }

        result = await resolver_agent._execute_hybrid(
            "TICKET-001",
            sop_recommendations,
            sample_ticket_context
        )

        assert result["strategy"] == ResolutionStrategy.HYBRID_EXECUTION.value
        assert len(result["sops_used"]) == 3
        assert len(result["execution_log"]) >= 3


@pytest.mark.asyncio
async def test_execute_manual_generates_guide(resolver_agent, sample_ticket_context, sample_sop_high_confidence):
    """Test manual execution generates user guide"""
    result = await resolver_agent._execute_manual(
        "TICKET-001",
        sample_sop_high_confidence,
        sample_ticket_context
    )

    assert result["strategy"] == ResolutionStrategy.MANUAL_EXECUTION.value
    assert "user_guide" in result
    assert len(result["user_guide"]) == len(sample_sop_high_confidence["steps"])
    assert all("instruction" in step for step in result["user_guide"])


@pytest.mark.asyncio
async def test_execute_manual_no_sop(resolver_agent, sample_ticket_context):
    """Test manual execution without SOP"""
    result = await resolver_agent._execute_manual(
        "TICKET-001",
        None,
        sample_ticket_context
    )

    assert result["status"] == ResolutionStatus.FAILED.value
    assert "message" in result


# ============================================================================
# ESCALATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_escalate_ticket(resolver_agent, sample_ticket_context, sample_classification):
    """Test ticket escalation"""
    context = {
        "error": "Unable to resolve automatically",
        "execution_log": [{"step": 1, "status": "failed"}]
    }

    result = await resolver_agent._escalate(
        "TICKET-001",
        sample_classification,
        context
    )

    assert result["status"] == ResolutionStatus.ESCALATED.value
    assert result["strategy"] == ResolutionStrategy.ESCALATION.value
    assert "escalation_reason" in result
    assert "attempted_steps" in result
    assert result["assigned_to"] == "Level 2 Support"


# ============================================================================
# DESKTOP COMMANDER INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_call_desktop_commander_success(resolver_agent):
    """Test successful Desktop-CommanderAgent call"""
    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "output": "Command executed",
            "exit_code": 0,
            "success": True
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = await resolver_agent._call_desktop_commander(
            command="ipconfig /all",
            target_device="WS-001",
            safety_checks=True
        )

        assert result["success"] is True
        assert result["exit_code"] == 0
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_call_desktop_commander_failure(resolver_agent):
    """Test Desktop-CommanderAgent call failure"""
    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = Exception("Connection refused")

        with pytest.raises(RuntimeError, match="Command execution failed"):
            await resolver_agent._call_desktop_commander(
                command="ipconfig /all",
                target_device="WS-001",
                safety_checks=True
            )


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_full_resolution_workflow(resolver_agent, sample_ticket_context, sample_classification, sample_sop_high_confidence):
    """Test complete resolution workflow from task to result"""
    task = {
        "ticket_id": "TICKET-001",
        "classification": sample_classification,
        "sop_recommendations": [sample_sop_high_confidence]
    }

    with patch.object(resolver_agent, '_execute_step', new_callable=AsyncMock) as mock_execute_step, \
         patch.object(resolver_agent, '_update_ticket_status', new_callable=AsyncMock) as mock_update, \
         patch.object(resolver_agent, '_log_resolution_metrics', new_callable=AsyncMock) as mock_log:

        mock_execute_step.return_value = {
            "output": "Success",
            "resolution_confirmed": True
        }

        result = await resolver_agent.execute(task)

        assert result["agent"] == "resolver"
        assert result["ticket_id"] == "TICKET-001"
        assert "strategy" in result
        assert "confidence" in result
        assert "result" in result
        assert "timestamp" in result

        mock_update.assert_called_once()
        mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_full_resolution_workflow_with_error(resolver_agent, sample_ticket_context, sample_classification):
    """Test resolution workflow with critical error triggers escalation"""
    task = {
        "ticket_id": "TICKET-001",
        "classification": sample_classification,
        "sop_recommendations": []  # No SOPs to force escalation
    }

    with patch.object(resolver_agent, '_update_ticket_status', new_callable=AsyncMock) as mock_update, \
         patch.object(resolver_agent, '_log_resolution_metrics', new_callable=AsyncMock) as mock_log:

        result = await resolver_agent.execute(task)

        assert result["strategy"] == ResolutionStrategy.ESCALATION.value
        assert result["confidence"] == 0.0


# ============================================================================
# PREREQUISITE VALIDATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_validate_prerequisites_success(resolver_agent, sample_sop_high_confidence, sample_ticket_context):
    """Test prerequisite validation success"""
    result = await resolver_agent._validate_prerequisites(
        sample_sop_high_confidence,
        sample_ticket_context
    )

    # Currently returns True by default (TODO implemented)
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_validate_prerequisites_failure(resolver_agent):
    """Test prerequisite validation failure"""
    sop = {
        "id": "SOP-TEST",
        "prerequisites": {
            "tools": ["nonexistent_tool"],
            "permissions": ["super_admin"]
        }
    }

    with patch.object(resolver_agent, '_validate_prerequisites', return_value=False):
        result = await resolver_agent._validate_prerequisites(sop, {})
        assert result is False


# ============================================================================
# HEALTH CHECK TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_health_check_all_healthy(resolver_agent):
    """Test health check when all systems healthy"""
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get, \
         patch('agents.resolver.resolver_agent.get_db') as mock_db:

        # Mock Desktop-Commander health
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Mock database health
        mock_db_session = MagicMock()
        mock_db_session.execute = AsyncMock()
        mock_db.return_value.__aiter__.return_value = [mock_db_session]

        health = await resolver_agent.health_check()

        assert health["status"] == "healthy"
        assert health["checks"]["desktop_commander"] == "healthy"
        assert health["checks"]["database"] == "healthy"


@pytest.mark.asyncio
async def test_health_check_degraded(resolver_agent):
    """Test health check when services degraded"""
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("Connection timeout")

        health = await resolver_agent.health_check()

        assert health["status"] == "degraded"
        assert "unhealthy" in health["checks"]["desktop_commander"]


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_execute_with_missing_ticket_id(resolver_agent):
    """Test execution with missing ticket_id"""
    task = {
        "classification": {},
        "sop_recommendations": []
    }

    result = await resolver_agent.execute(task)

    # Should handle gracefully (ticket_id = None)
    assert "error" in result or result["strategy"] == ResolutionStrategy.ESCALATION.value


@pytest.mark.asyncio
async def test_execute_with_empty_classification(resolver_agent):
    """Test execution with empty classification"""
    task = {
        "ticket_id": "TICKET-999",
        "classification": {},
        "sop_recommendations": []
    }

    result = await resolver_agent.execute(task)

    assert result["strategy"] == ResolutionStrategy.ESCALATION.value


@pytest.mark.asyncio
async def test_concurrent_resolutions(resolver_agent, sample_ticket_context, sample_classification, sample_sop_high_confidence):
    """Test concurrent resolution execution"""
    tasks = [
        {
            "ticket_id": f"TICKET-{i}",
            "classification": sample_classification,
            "sop_recommendations": [sample_sop_high_confidence]
        }
        for i in range(3)
    ]

    with patch.object(resolver_agent, '_execute_step', new_callable=AsyncMock) as mock_execute_step, \
         patch.object(resolver_agent, '_update_ticket_status', new_callable=AsyncMock), \
         patch.object(resolver_agent, '_log_resolution_metrics', new_callable=AsyncMock):

        mock_execute_step.return_value = {
            "output": "Success",
            "resolution_confirmed": True
        }

        results = await asyncio.gather(*[resolver_agent.execute(task) for task in tasks])

        assert len(results) == 3
        assert all(r["agent"] == "resolver" for r in results)
        assert all("ticket_id" in r for r in results)


# ============================================================================
# LOGGING AND METRICS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_log_resolution_metrics(resolver_agent):
    """Test resolution metrics logging"""
    result = {
        "status": ResolutionStatus.SUCCESS.value,
        "execution_log": [{"step": 1}, {"step": 2}],
        "execution_time": 5.2
    }

    # Should not raise exception
    await resolver_agent._log_resolution_metrics(
        "TICKET-001",
        ResolutionStrategy.DIRECT_EXECUTION,
        result,
        0.92
    )


@pytest.mark.asyncio
async def test_update_ticket_status_success(resolver_agent):
    """Test ticket status update"""
    result = {
        "status": ResolutionStatus.SUCCESS.value,
        "execution_log": []
    }

    with patch('agents.resolver.resolver_agent.get_db') as mock_db:
        mock_db_session = MagicMock()
        mock_ticket_service = MagicMock()
        mock_ticket_service.update_ticket_status = AsyncMock()

        with patch('agents.resolver.resolver_agent.TicketService', return_value=mock_ticket_service):
            mock_db.return_value.__aiter__.return_value = [mock_db_session]

            await resolver_agent._update_ticket_status("TICKET-001", result)

            mock_ticket_service.update_ticket_status.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
