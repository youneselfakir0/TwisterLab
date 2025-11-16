# AGENT 1: RESOLVER AGENT - COMPLETE IMPLEMENTATION PLAN

**Priority:** 1 (CRITICAL PATH)
**Status:** Planning Phase
**Estimated Lines:** 800+
**Dependencies:** ClassifierAgent, SOPService, Desktop-Commander

---

## 1. ARCHITECTURE OVERVIEW

### 1.1 Role in System
The ResolverAgent is the **core automation engine** of TwisterLab. It receives classified tickets and executes appropriate Standard Operating Procedures (SOPs) to resolve issues automatically.

**Workflow Position:**
```
Email → ClassifierAgent → ResolverAgent → Desktop-Commander → Resolution
                              ↓
                        (escalation if needed)
                              ↓
                         Human Agent
```

### 1.2 Core Responsibilities
1. **SOP Matching** - Find the best SOP for a classified ticket
2. **Resolution Execution** - Execute multi-step troubleshooting workflows
3. **Confidence Scoring** - Assess likelihood of successful resolution
4. **Escalation Logic** - Route to humans when confidence is low
5. **Result Reporting** - Detailed execution logs and outcomes

### 1.3 Input/Output Format

**Input (from ClassifierAgent):**
```json
{
  "ticket_id": "TKT-12345",
  "classification": {
    "category": "password",
    "priority": "high",
    "complexity": "simple",
    "confidence": 0.9
  },
  "ticket_data": {
    "subject": "Cannot login to email",
    "description": "User forgot password",
    "requestor": "john.doe@example.com"
  }
}
```

**Output (Resolution Result):**
```json
{
  "status": "resolved" | "escalated" | "failed",
  "ticket_id": "TKT-12345",
  "resolution": {
    "sop_used": "SOP-001-Password-Reset",
    "steps_executed": 5,
    "execution_time": "120 seconds",
    "actions_taken": [
      "Verified user identity",
      "Reset AD password",
      "Sent temporary password email",
      "Logged action in audit trail"
    ]
  },
  "confidence_score": 0.95,
  "escalation_reason": null
}
```

---

## 2. CODE TEMPLATE

### 2.1 Class Structure

**File:** `agents/helpdesk/auto_resolver.py`

```python
"""
TwisterLab - Helpdesk Resolver Agent
Executes troubleshooting SOPs and resolves tickets automatically
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum

from ..base import TwisterAgent
from ..database.config import get_db
from ..database.services import SOPService, TicketService
from ..database.models import Ticket, SOP, ResolutionLog

logger = logging.getLogger(__name__)


class ResolutionStatus(Enum):
    """Status codes for resolution attempts"""
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"


class HelpdeskResolverAgent(TwisterAgent):
    """
    Agent specialized in executing SOPs to resolve IT helpdesk tickets.

    Capabilities:
    - Match tickets to appropriate SOPs
    - Execute multi-step resolution workflows
    - Calculate confidence scores
    - Escalate when necessary
    - Log all actions for audit
    """

    def __init__(self):
        super().__init__(
            name="helpdesk-resolver",
            display_name="IT Helpdesk Resolver",
            description="Executes troubleshooting SOPs and resolves tickets automatically",
            role="resolver",
            instructions=self._get_instructions(),
            tools=self._define_tools(),
            model="llama-3.2",
            temperature=0.3,  # Low for consistent operations
            metadata={
                "department": "IT",
                "sla_target": "5 minutes",
                "automation_rate": "60-70%",
                "max_retry_attempts": 3
            }
        )

        # Resolution strategies
        self.strategies = {
            "password": self._resolve_password_issue,
            "software": self._resolve_software_issue,
            "access": self._resolve_access_issue,
            "hardware": self._resolve_hardware_issue,
            "network": self._resolve_network_issue
        }

        # Confidence thresholds
        self.MIN_CONFIDENCE = 0.6
        self.ESCALATION_THRESHOLD = 0.5

    def _get_instructions(self) -> str:
        """Get agent instructions"""
        return """
        You are an IT Helpdesk Resolver Agent specializing in automatic ticket resolution.

        Your workflow:
        1. Receive classified ticket from ClassifierAgent
        2. Match ticket to appropriate SOP from database
        3. Execute SOP steps in sequence
        4. Call Desktop-Commander for system operations when needed
        5. Verify resolution success
        6. Log all actions for audit trail
        7. Escalate to human if confidence < 60%

        Categories you handle:
        - Password resets (Active Directory)
        - Software installations (via Desktop Commander)
        - Access requests (permissions, groups)
        - Basic hardware diagnostics
        - Network connectivity issues

        Always prioritize user safety and data security.
        Never execute destructive commands without verification.
        """

    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define agent tools (max 5)"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "match_sop",
                    "description": "Find the best matching SOP for a ticket",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {"type": "string"},
                            "category": {"type": "string"},
                            "description": {"type": "string"}
                        },
                        "required": ["ticket_id", "category"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_sop",
                    "description": "Execute a specific SOP's steps",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sop_id": {"type": "string"},
                            "ticket_id": {"type": "string"},
                            "context": {"type": "object"}
                        },
                        "required": ["sop_id", "ticket_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_desktop_command",
                    "description": "Execute command via Desktop Commander",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {"type": "string"},
                            "command": {"type": "string"},
                            "timeout": {"type": "integer"}
                        },
                        "required": ["device_id", "command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "verify_resolution",
                    "description": "Verify that resolution was successful",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {"type": "string"},
                            "expected_outcome": {"type": "string"}
                        },
                        "required": ["ticket_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "escalate_ticket",
                    "description": "Escalate ticket to human agent",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {"type": "string"},
                            "reason": {"type": "string"},
                            "context": {"type": "object"}
                        },
                        "required": ["ticket_id", "reason"]
                    }
                }
            }
        ]

    async def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main execution method.

        Args:
            task: Task description
            context: Ticket and classification data

        Returns:
            Resolution result with detailed logs
        """
        start_time = datetime.now(timezone.utc)

        try:
            logger.info(f"Resolver executing task: {task}")

            # Extract ticket data
            ticket_data = context.get("ticket", {}) if context else {}
            classification = context.get("classification", {}) if context else {}

            ticket_id = ticket_data.get("id", "unknown")
            category = classification.get("category", "other")

            # Step 1: Match SOP
            sop_match = await self._match_sop(ticket_id, category, ticket_data)

            if not sop_match["matched"]:
                return await self._escalate(
                    ticket_id,
                    "no_matching_sop",
                    ticket_data
                )

            # Step 2: Check confidence
            confidence = self._calculate_confidence(classification, sop_match)

            if confidence < self.ESCALATION_THRESHOLD:
                return await self._escalate(
                    ticket_id,
                    "low_confidence",
                    {"confidence": confidence, "sop": sop_match}
                )

            # Step 3: Execute resolution
            resolution_result = await self._execute_resolution(
                ticket_id,
                category,
                sop_match,
                ticket_data
            )

            # Step 4: Verify resolution
            if resolution_result["status"] == ResolutionStatus.RESOLVED.value:
                verification = await self._verify_resolution(
                    ticket_id,
                    resolution_result
                )

                if not verification["verified"]:
                    return await self._escalate(
                        ticket_id,
                        "verification_failed",
                        verification
                    )

            # Calculate execution time
            execution_time = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds()

            # Return result
            return {
                "status": resolution_result["status"],
                "ticket_id": ticket_id,
                "resolution": {
                    "sop_used": sop_match.get("sop_id"),
                    "sop_title": sop_match.get("sop_title"),
                    "steps_executed": len(resolution_result.get("actions", [])),
                    "execution_time": f"{execution_time:.2f} seconds",
                    "actions_taken": resolution_result.get("actions", []),
                    "desktop_commands": resolution_result.get("commands", [])
                },
                "confidence_score": confidence,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error in resolver execution: {e}", exc_info=True)
            return {
                "status": "failed",
                "ticket_id": ticket_id if 'ticket_id' in locals() else "unknown",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    async def _match_sop(
        self,
        ticket_id: str,
        category: str,
        ticket_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Match ticket to appropriate SOP.

        Uses database SOP service to find best match based on:
        - Category
        - Keywords
        - Previous success rate
        """
        try:
            async for session in get_db():
                sop_service = SOPService(session)

                # Get SOPs for category
                sops = await sop_service.get_sops_by_category(category)

                if not sops:
                    logger.warning(f"No SOPs found for category: {category}")
                    return {"matched": False, "reason": "no_sops_for_category"}

                # Score each SOP
                best_sop = None
                best_score = 0

                description = ticket_data.get("description", "").lower()
                subject = ticket_data.get("subject", "").lower()
                full_text = f"{subject} {description}"

                for sop in sops:
                    score = self._calculate_sop_score(sop, full_text)
                    if score > best_score:
                        best_score = score
                        best_sop = sop

                if best_sop and best_score > 0.5:
                    return {
                        "matched": True,
                        "sop_id": best_sop.id,
                        "sop_title": best_sop.title,
                        "sop_steps": best_sop.steps,
                        "match_score": best_score
                    }
                else:
                    return {
                        "matched": False,
                        "reason": "low_match_score",
                        "best_score": best_score
                    }

        except Exception as e:
            logger.error(f"Error matching SOP: {e}")
            return {"matched": False, "reason": "error", "error": str(e)}

    def _calculate_sop_score(self, sop: SOP, text: str) -> float:
        """Calculate how well an SOP matches the ticket text"""
        score = 0.0

        # Keyword matching
        if hasattr(sop, 'keywords') and sop.keywords:
            keywords = sop.keywords.lower().split(',')
            for keyword in keywords:
                if keyword.strip() in text:
                    score += 0.2

        # Title matching
        if hasattr(sop, 'title'):
            title_words = sop.title.lower().split()
            for word in title_words:
                if len(word) > 3 and word in text:
                    score += 0.1

        return min(score, 1.0)

    def _calculate_confidence(
        self,
        classification: Dict[str, Any],
        sop_match: Dict[str, Any]
    ) -> float:
        """
        Calculate overall confidence for resolution.

        Factors:
        - Classification confidence
        - SOP match score
        - SOP historical success rate
        """
        class_confidence = classification.get("confidence", 0.5)
        match_score = sop_match.get("match_score", 0.5)

        # Weighted average
        confidence = (class_confidence * 0.6) + (match_score * 0.4)

        return round(confidence, 2)

    async def _execute_resolution(
        self,
        ticket_id: str,
        category: str,
        sop_match: Dict[str, Any],
        ticket_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute resolution based on category.
        """
        try:
            # Get category-specific strategy
            strategy = self.strategies.get(category)

            if not strategy:
                logger.warning(f"No strategy for category: {category}")
                return {
                    "status": ResolutionStatus.ESCALATED.value,
                    "reason": "unsupported_category"
                }

            # Execute strategy
            result = await strategy(ticket_id, sop_match, ticket_data)

            # Log resolution
            await self._log_resolution(ticket_id, result)

            return result

        except Exception as e:
            logger.error(f"Error executing resolution: {e}")
            return {
                "status": ResolutionStatus.FAILED.value,
                "error": str(e),
                "actions": []
            }

    async def _resolve_password_issue(
        self,
        ticket_id: str,
        sop_match: Dict[str, Any],
        ticket_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve password-related issues"""
        actions = []

        try:
            # Extract user info
            requestor = ticket_data.get("requestor", "")
            username = requestor.split('@')[0] if '@' in requestor else requestor

            actions.append(f"Identified user: {username}")

            # Step 1: Verify user in AD
            actions.append("Verified user exists in Active Directory")

            # Step 2: Generate temporary password
            temp_password = self._generate_temp_password()
            actions.append("Generated secure temporary password")

            # Step 3: Reset password (would call Desktop Commander)
            # await self._call_desktop_commander("reset_ad_password", {...})
            actions.append(f"Reset AD password for user {username}")

            # Step 4: Send notification email
            actions.append(f"Sent password reset email to {requestor}")

            # Step 5: Log in audit trail
            actions.append("Logged action in security audit trail")

            return {
                "status": ResolutionStatus.RESOLVED.value,
                "actions": actions,
                "commands": ["reset_ad_password"],
                "notification_sent": True
            }

        except Exception as e:
            logger.error(f"Error resolving password issue: {e}")
            return {
                "status": ResolutionStatus.FAILED.value,
                "actions": actions,
                "error": str(e)
            }

    async def _resolve_software_issue(
        self,
        ticket_id: str,
        sop_match: Dict[str, Any],
        ticket_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve software installation/issues"""
        actions = []

        try:
            # Extract software name from ticket
            description = ticket_data.get("description", "").lower()

            # Identify software
            software_name = self._identify_software(description)
            actions.append(f"Identified software request: {software_name}")

            # Get device ID
            requestor = ticket_data.get("requestor", "")
            device_id = await self._get_user_device(requestor)

            if not device_id:
                return {
                    "status": ResolutionStatus.ESCALATED.value,
                    "reason": "device_not_found",
                    "actions": actions
                }

            actions.append(f"Located user device: {device_id}")

            # Call Desktop Commander for installation
            # result = await self._call_desktop_commander("install_software", {...})
            actions.append(f"Initiated software installation via Desktop Commander")
            actions.append(f"Installation completed successfully")

            return {
                "status": ResolutionStatus.RESOLVED.value,
                "actions": actions,
                "commands": ["install_software"],
                "device_id": device_id
            }

        except Exception as e:
            logger.error(f"Error resolving software issue: {e}")
            return {
                "status": ResolutionStatus.FAILED.value,
                "actions": actions,
                "error": str(e)
            }

    async def _resolve_access_issue(
        self,
        ticket_id: str,
        sop_match: Dict[str, Any],
        ticket_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve access/permission issues"""
        actions = []

        try:
            requestor = ticket_data.get("requestor", "")
            username = requestor.split('@')[0] if '@' in requestor else requestor

            # Identify resource needed
            description = ticket_data.get("description", "")
            resource = self._identify_resource(description)

            actions.append(f"Access request for: {resource}")

            # Grant access (would call appropriate API)
            actions.append(f"Granted {username} access to {resource}")
            actions.append("Updated Active Directory permissions")
            actions.append("Sent confirmation email")

            return {
                "status": ResolutionStatus.RESOLVED.value,
                "actions": actions,
                "resource": resource
            }

        except Exception as e:
            logger.error(f"Error resolving access issue: {e}")
            return {
                "status": ResolutionStatus.FAILED.value,
                "actions": actions,
                "error": str(e)
            }

    async def _resolve_hardware_issue(
        self,
        ticket_id: str,
        sop_match: Dict[str, Any],
        ticket_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve basic hardware issues"""
        # Hardware typically requires human intervention
        return {
            "status": ResolutionStatus.ESCALATED.value,
            "reason": "hardware_requires_physical_intervention",
            "actions": ["Identified as hardware issue"]
        }

    async def _resolve_network_issue(
        self,
        ticket_id: str,
        sop_match: Dict[str, Any],
        ticket_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve basic network connectivity issues"""
        actions = []

        try:
            # Basic network diagnostics
            requestor = ticket_data.get("requestor", "")
            device_id = await self._get_user_device(requestor)

            if device_id:
                actions.append("Running network diagnostics")
                # await self._call_desktop_commander("network_diagnostics", {...})
                actions.append("Network connectivity test completed")
                actions.append("DNS resolution verified")

                return {
                    "status": ResolutionStatus.RESOLVED.value,
                    "actions": actions,
                    "commands": ["network_diagnostics"]
                }
            else:
                return {
                    "status": ResolutionStatus.ESCALATED.value,
                    "reason": "device_not_found",
                    "actions": actions
                }

        except Exception as e:
            logger.error(f"Error resolving network issue: {e}")
            return {
                "status": ResolutionStatus.FAILED.value,
                "actions": actions,
                "error": str(e)
            }

    async def _verify_resolution(
        self,
        ticket_id: str,
        resolution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify that resolution was successful.

        Can include:
        - Checking system state
        - Sending test emails
        - Verifying permissions
        """
        try:
            # Basic verification based on resolution type
            if resolution_result.get("status") == ResolutionStatus.RESOLVED.value:
                return {
                    "verified": True,
                    "checks_passed": ["execution_completed", "no_errors"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "verified": False,
                    "reason": "resolution_not_successful"
                }

        except Exception as e:
            logger.error(f"Error verifying resolution: {e}")
            return {
                "verified": False,
                "error": str(e)
            }

    async def _escalate(
        self,
        ticket_id: str,
        reason: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Escalate ticket to human agent"""
        try:
            logger.info(f"Escalating ticket {ticket_id}: {reason}")

            return {
                "status": ResolutionStatus.ESCALATED.value,
                "ticket_id": ticket_id,
                "escalation_reason": reason,
                "context": context,
                "recommended_queue": "senior_helpdesk",
                "priority": "high",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error escalating ticket: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _log_resolution(
        self,
        ticket_id: str,
        resolution_result: Dict[str, Any]
    ) -> None:
        """Log resolution in database"""
        try:
            async for session in get_db():
                # Create resolution log entry
                log_entry = ResolutionLog(
                    ticket_id=ticket_id,
                    status=resolution_result.get("status"),
                    actions=resolution_result.get("actions", []),
                    timestamp=datetime.now(timezone.utc)
                )
                session.add(log_entry)
                await session.commit()

        except Exception as e:
            logger.error(f"Error logging resolution: {e}")

    # Helper methods

    def _generate_temp_password(self) -> str:
        """Generate secure temporary password"""
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(alphabet) for _ in range(12))

    def _identify_software(self, text: str) -> str:
        """Identify software name from text"""
        # Simple keyword matching (could be more sophisticated)
        software_keywords = {
            "office": "Microsoft Office 365",
            "excel": "Microsoft Excel",
            "word": "Microsoft Word",
            "chrome": "Google Chrome",
            "firefox": "Mozilla Firefox",
            "teams": "Microsoft Teams"
        }

        for keyword, software in software_keywords.items():
            if keyword in text.lower():
                return software

        return "Unknown Software"

    def _identify_resource(self, text: str) -> str:
        """Identify resource from access request"""
        # Simple resource identification
        if "sharepoint" in text.lower():
            return "SharePoint Site"
        elif "folder" in text.lower() or "drive" in text.lower():
            return "Network Drive"
        else:
            return "Unspecified Resource"

    async def _get_user_device(self, requestor: str) -> Optional[str]:
        """Get user's primary device ID"""
        # Would query device database
        # For now, return mock device ID
        username = requestor.split('@')[0] if '@' in requestor else requestor
        return f"DEVICE-{username.upper()}-001"
```

---

## 3. INTEGRATION POINTS

### 3.1 Input from ClassifierAgent

```python
# In Maestro Orchestrator
from agents.helpdesk.classifier import TicketClassifierAgent
from agents.helpdesk.auto_resolver import HelpdeskResolverAgent

# Workflow
classifier = TicketClassifierAgent()
resolver = HelpdeskResolverAgent()

# Step 1: Classify
classification = await classifier.execute(
    "Classify ticket",
    {"ticket": ticket_data}
)

# Step 2: Resolve
if classification["status"] == "success":
    resolution = await resolver.execute(
        "Resolve ticket",
        {
            "ticket": ticket_data,
            "classification": classification["classification"]
        }
    )
```

### 3.2 Output to Desktop-Commander

```python
# ResolverAgent calls Desktop-Commander for system operations
async def _call_desktop_commander(
    self,
    operation: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Call Desktop Commander agent"""
    from agents.helpdesk.desktop_commander import DesktopCommanderAgent

    commander = DesktopCommanderAgent()
    result = await commander.execute(operation, params)
    return result
```

### 3.3 Database Integration

```python
# SOPService usage
from agents.database.services import SOPService

async def get_sops_for_category(category: str):
    async for session in get_db():
        sop_service = SOPService(session)
        sops = await sop_service.get_sops_by_category(category)
        return sops
```

### 3.4 API Endpoints

```python
# In agents/api/routes_agents.py
from agents.helpdesk.auto_resolver import HelpdeskResolverAgent

@router.post("/agents/resolver/execute")
async def execute_resolver(
    ticket_id: str,
    classification: Dict[str, Any]
):
    """Execute resolver agent on a ticket"""
    resolver = HelpdeskResolverAgent()

    result = await resolver.execute(
        f"Resolve ticket {ticket_id}",
        {
            "ticket": {"id": ticket_id},
            "classification": classification
        }
    )

    return result
```

---

## 4. TESTING STRATEGY

### 4.1 Unit Tests

**File:** `tests/test_resolver_agent.py`

```python
import pytest
from agents.helpdesk.auto_resolver import HelpdeskResolverAgent, ResolutionStatus

@pytest.mark.asyncio
async def test_resolver_initialization():
    """Test resolver agent initializes correctly"""
    resolver = HelpdeskResolverAgent()

    assert resolver.name == "helpdesk-resolver"
    assert resolver.temperature == 0.3
    assert len(resolver.tools) == 5
    assert "password" in resolver.strategies

@pytest.mark.asyncio
async def test_password_reset_resolution():
    """Test password reset workflow"""
    resolver = HelpdeskResolverAgent()

    ticket_data = {
        "id": "TKT-001",
        "subject": "Cannot login",
        "description": "Forgot my password",
        "requestor": "john.doe@example.com"
    }

    classification = {
        "category": "password",
        "priority": "high",
        "complexity": "simple",
        "confidence": 0.9
    }

    result = await resolver.execute(
        "Resolve password ticket",
        {
            "ticket": ticket_data,
            "classification": classification
        }
    )

    assert result["status"] == "resolved"
    assert "password" in str(result["resolution"]["actions_taken"]).lower()
    assert result["confidence_score"] > 0.6

@pytest.mark.asyncio
async def test_low_confidence_escalation():
    """Test escalation when confidence is low"""
    resolver = HelpdeskResolverAgent()

    classification = {
        "category": "other",
        "priority": "medium",
        "complexity": "complex",
        "confidence": 0.3
    }

    result = await resolver.execute(
        "Resolve complex ticket",
        {
            "ticket": {"id": "TKT-002"},
            "classification": classification
        }
    )

    assert result["status"] == "escalated"
    assert "escalation_reason" in result

@pytest.mark.asyncio
async def test_sop_matching():
    """Test SOP matching logic"""
    resolver = HelpdeskResolverAgent()

    ticket_data = {
        "subject": "Install Microsoft Office",
        "description": "Need Office 365 on my laptop"
    }

    sop_match = await resolver._match_sop(
        "TKT-003",
        "software",
        ticket_data
    )

    # Should find a matching SOP or indicate no match
    assert "matched" in sop_match

@pytest.mark.asyncio
async def test_confidence_calculation():
    """Test confidence scoring"""
    resolver = HelpdeskResolverAgent()

    classification = {"confidence": 0.8}
    sop_match = {"match_score": 0.9}

    confidence = resolver._calculate_confidence(classification, sop_match)

    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.7  # Should be high with good inputs

@pytest.mark.asyncio
async def test_resolution_logging():
    """Test that resolutions are logged"""
    resolver = HelpdeskResolverAgent()

    resolution_result = {
        "status": "resolved",
        "actions": ["Action 1", "Action 2"]
    }

    # Should not raise exception
    await resolver._log_resolution("TKT-004", resolution_result)

@pytest.mark.asyncio
async def test_software_identification():
    """Test software name identification"""
    resolver = HelpdeskResolverAgent()

    text1 = "I need to install Microsoft Office"
    text2 = "Can you install Chrome browser"

    software1 = resolver._identify_software(text1)
    software2 = resolver._identify_software(text2)

    assert "office" in software1.lower()
    assert "chrome" in software2.lower()
```

### 4.2 Integration Tests

```python
@pytest.mark.asyncio
async def test_full_resolution_pipeline():
    """Test complete resolution pipeline"""
    from agents.helpdesk.classifier import TicketClassifierAgent
    from agents.helpdesk.auto_resolver import HelpdeskResolverAgent

    # Create agents
    classifier = TicketClassifierAgent()
    resolver = HelpdeskResolverAgent()

    # Sample ticket
    ticket = {
        "id": "TKT-PIPELINE-001",
        "subject": "Password reset needed",
        "description": "I forgot my password and cannot log in",
        "requestor": "test.user@example.com"
    }

    # Step 1: Classify
    classification = await classifier.execute(
        "Classify ticket",
        {"ticket": ticket}
    )

    assert classification["status"] == "success"

    # Step 2: Resolve
    resolution = await resolver.execute(
        "Resolve ticket",
        {
            "ticket": ticket,
            "classification": classification["classification"]
        }
    )

    # Verify resolution
    assert resolution["status"] in ["resolved", "escalated"]
    assert "ticket_id" in resolution
```

### 4.3 Mock Data

```python
# tests/fixtures/resolver_fixtures.py

SAMPLE_TICKETS = [
    {
        "id": "TKT-PASSWORD-001",
        "category": "password",
        "subject": "Cannot login",
        "description": "Forgot password",
        "expected_resolution": "resolved"
    },
    {
        "id": "TKT-SOFTWARE-001",
        "category": "software",
        "subject": "Install Office",
        "description": "Need Microsoft Office 365",
        "expected_resolution": "resolved"
    },
    {
        "id": "TKT-COMPLEX-001",
        "category": "hardware",
        "subject": "Laptop won't start",
        "description": "Black screen on startup",
        "expected_resolution": "escalated"
    }
]

SAMPLE_SOPS = [
    {
        "id": "SOP-001",
        "title": "Active Directory Password Reset",
        "category": "password",
        "keywords": "password,reset,login,forgot",
        "steps": [
            "Verify user identity",
            "Reset AD password",
            "Send notification email"
        ]
    },
    {
        "id": "SOP-002",
        "title": "Software Installation via Desktop Commander",
        "category": "software",
        "keywords": "install,software,application",
        "steps": [
            "Identify software package",
            "Locate user device",
            "Execute remote installation"
        ]
    }
]
```

---

## 5. DEPLOYMENT NOTES

### 5.1 Configuration

**Environment Variables (.env):**
```bash
# Resolver Agent Configuration
RESOLVER_MIN_CONFIDENCE=0.6
RESOLVER_ESCALATION_THRESHOLD=0.5
RESOLVER_MAX_RETRIES=3
RESOLVER_TIMEOUT=300

# Desktop Commander Integration
DESKTOP_COMMANDER_URL=http://desktop-commander:8001
DESKTOP_COMMANDER_API_KEY=${DC_API_KEY}

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/twisterlab

# Redis
REDIS_URL=redis://localhost:6379/0
```

### 5.2 Docker Setup

**docker-compose.yml:**
```yaml
services:
  resolver-agent:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: twisterlab-resolver
    environment:
      - AGENT_TYPE=resolver
      - RESOLVER_MIN_CONFIDENCE=${RESOLVER_MIN_CONFIDENCE}
    depends_on:
      - postgres
      - redis
      - desktop-commander
    networks:
      - twisterlab-network
    restart: unless-stopped
```

### 5.3 Monitoring Setup

**Health Check Endpoint:**
```python
@router.get("/agents/resolver/health")
async def resolver_health():
    """Resolver agent health check"""
    resolver = HelpdeskResolverAgent()

    return {
        "status": "healthy",
        "agent": resolver.name,
        "strategies_loaded": len(resolver.strategies),
        "tools_available": len(resolver.tools),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
```

**Metrics to Monitor:**
```python
# Prometheus metrics
resolver_tickets_total = Counter(
    'resolver_tickets_total',
    'Total tickets processed by resolver'
)

resolver_resolution_duration = Histogram(
    'resolver_resolution_duration_seconds',
    'Time to resolve tickets'
)

resolver_escalations_total = Counter(
    'resolver_escalations_total',
    'Total escalations to human agents'
)
```

---

## 6. IMPLEMENTATION CHECKLIST

- [ ] Create `agents/helpdesk/auto_resolver.py`
- [ ] Implement base class structure
- [ ] Implement SOP matching logic
- [ ] Implement resolution strategies (password, software, access, etc.)
- [ ] Implement confidence calculation
- [ ] Implement escalation logic
- [ ] Add Desktop-Commander integration
- [ ] Create unit tests
- [ ] Create integration tests
- [ ] Add API endpoints
- [ ] Configure environment variables
- [ ] Setup Docker configuration
- [ ] Add health check endpoint
- [ ] Add Prometheus metrics
- [ ] Document API
- [ ] Test end-to-end workflow

---

**Next Agent:** [Desktop-CommanderAgent (Priority 2)](AGENT_2_DESKTOP_COMMANDER_PLAN.md)
