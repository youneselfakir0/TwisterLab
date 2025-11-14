"""
Tests for Real Agents - Production Validation
=============================================

Simple tests to validate real agent functionality for production deployment.
"""

import pytest
import asyncio
from agents.real.real_backup_agent import RealBackupAgent
from agents.real.real_monitoring_agent import RealMonitoringAgent
from agents.real.real_sync_agent import RealSyncAgent
from agents.real.real_classifier_agent import RealClassifierAgent
from agents.real.real_resolver_agent import RealResolverAgent
from agents.real.real_desktop_commander_agent import RealDesktopCommanderAgent
from agents.real.real_maestro_agent import RealMaestroAgent


@pytest.mark.asyncio
async def test_real_backup_agent():
    """Test RealBackupAgent basic functionality"""
    agent = RealBackupAgent(backup_dir="/tmp/test_backups")

    # Test list_backups operation (should work without external deps)
    result = await agent.execute({"operation": "list_backups"})
    assert "status" in result
    assert "backups" in result


@pytest.mark.asyncio
async def test_real_monitoring_agent():
    """Test RealMonitoringAgent basic functionality"""
    agent = RealMonitoringAgent()

    # Test basic execution
    result = await agent.execute({"operation": "health_check"})
    assert result["status"] == "success"
    assert "health_status" in result


@pytest.mark.asyncio
async def test_real_sync_agent():
    """Test RealSyncAgent basic functionality"""
    agent = RealSyncAgent()

    # Test verify_consistency operation (should work without external deps)
    result = await agent.execute({"operation": "verify_consistency"})
    assert "status" in result


@pytest.mark.asyncio
async def test_real_classifier_agent():
    """Test RealClassifierAgent basic functionality"""
    agent = RealClassifierAgent()

    # Test ticket classification
    ticket = {
        "id": "TEST-001",
        "title": "Network issue",
        "description": "Cannot connect to internet"
    }

    result = await agent.execute({
        "operation": "classify_ticket",
        "ticket": ticket
    })
    assert result["status"] == "success"
    assert "classification" in result


@pytest.mark.asyncio
async def test_real_resolver_agent():
    """Test RealResolverAgent basic functionality"""
    agent = RealResolverAgent()

    # Test ticket resolution
    ticket = {
        "id": "TEST-001",
        "title": "Software issue",
        "description": "Application crashes on startup",
        "category": "software"
    }

    result = await agent.execute({
        "operation": "resolve_ticket",
        "ticket": ticket
    })
    assert result["status"] == "success"


@pytest.mark.asyncio
async def test_real_desktop_commander_agent():
    """Test RealDesktopCommanderAgent basic functionality"""
    agent = RealDesktopCommanderAgent()

    # Test with whitelisted command
    result = await agent.execute({
        "operation": "execute_command",
        "command": "ping",
        "args": ["127.0.0.1"]
    })
    assert "status" in result


@pytest.mark.asyncio
async def test_real_maestro_agent():
    """Test RealMaestroAgent basic functionality"""
    agent = RealMaestroAgent()

    # Test workflow orchestration
    ticket = {
        "id": "TEST-001",
        "title": "Test ticket",
        "description": "Test description"
    }

    result = await agent.execute({
        "operation": "orchestrate_workflow",
        "ticket": ticket
    })
    assert result["status"] == "success"
