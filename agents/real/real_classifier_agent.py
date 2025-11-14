"""
TwisterLab - Real Working Classifier Agent
Analyzes tickets and routes them to appropriate agents with LLM intelligence
"""
import asyncio
import re
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging

from agents.metrics import track_agent_execution, tickets_processed_total

logger = logging.getLogger(__name__)

# Import LLM client for intelligent classification
try:
    from agents.base.llm_client import ollama_client
    from agents.config import VALID_TICKET_CATEGORIES, AGENT_ROUTING_MAP
    from agents.metrics import record_classifier_llm, record_classifier_fallback, classifier_llm_error
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("⚠️ LLM client not available, falling back to keyword classification")


class RealClassifierAgent:
    """
    Real classifier agent that performs ACTUAL ticket classification.

    Operations:
    - classify_ticket: Analyze ticket and determine category, priority, routing
    - analyze_logs: Parse logs and create tickets automatically
    - detect_patterns: Find recurring issues
    """

    def __init__(self):
        self.name = "RealClassifierAgent"
        self.use_llm = LLM_AVAILABLE  # Use LLM if available

        # Classification rules (keyword-based FALLBACK)
        self.categories = {
            "network": ["network", "wifi", "ethernet", "connection", "internet", "dns", "ip", "ping"],
            "software": ["install", "software", "application", "app", "program", "update", "patch"],
            "hardware": ["hardware", "disk", "cpu", "memory", "ram", "gpu", "keyboard", "mouse"],
            "security": ["password", "security", "virus", "malware", "unauthorized", "breach"],
            "performance": ["slow", "performance", "lag", "freeze", "crash", "hang"],
            "database": ["database", "sql", "postgres", "redis", "query", "table"]
        }

        # Priority keywords
        self.priority_keywords = {
            "critical": ["down", "outage", "crash", "emergency", "critical", "production"],
            "high": ["urgent", "important", "asap", "blocking", "broken"],
            "medium": ["issue", "problem", "error", "bug", "not working"],
            "low": ["question", "request", "suggestion", "enhancement"]
        }

        # Routing map - USE CENTRAL CONFIG
        self.routing_map = AGENT_ROUTING_MAP

        self.classification_count = 0

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute classification operation.

        Args:
            context: Must contain 'operation' key
                Operations: classify_ticket, analyze_logs, detect_patterns

        Returns:
            Classification results
        """
        with track_agent_execution("classifier"):
            operation = context.get("operation", "classify_ticket")

            logger.info(f"🔍 RealClassifierAgent executing: {operation}")

            try:
                if operation == "classify_ticket":
                    ticket = context.get("ticket", {})
                    # Try LLM first, fallback to keywords if fails
                    if self.use_llm:
                        try:
                            result = await self._classify_ticket_llm(ticket)
                            if result.get("status") == "success":
                                tickets_processed_total.labels(agent_name="classifier", status="success").inc()
                            return result
                        except Exception as llm_error:
                            logger.warning(f"⚠️ LLM classification failed: {llm_error}, using keywords")
                            result = await self._classify_ticket_keywords(ticket)
                            if result.get("status") == "success":
                                tickets_processed_total.labels(agent_name="classifier", status="fallback").inc()
                            return result
                    else:
                        result = await self._classify_ticket_keywords(ticket)
                        if result.get("status") == "success":
                            tickets_processed_total.labels(agent_name="classifier", status="keyword").inc()
                        return result
                elif operation == "analyze_logs":
                    logs = context.get("logs", [])
                    return await self._analyze_logs(logs)
                elif operation == "detect_patterns":
                    tickets = context.get("tickets", [])
                    return await self._detect_patterns(tickets)
                else:
                    raise ValueError(f"Unknown operation: {operation}")

            except Exception as e:
                logger.error(f"❌ Classification failed: {e}", exc_info=True)
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

    async def _classify_ticket_llm(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a ticket using LLM (Ollama llama3.2:1b).

        Uses AI to intelligently determine:
        - Category (network, software, hardware, security, etc.)
        - Confidence score
        - Priority recommendation
        - Routing to appropriate agent
        """
        ticket_id = ticket.get("id", f"T-{self.classification_count:04d}")
        title = ticket.get("title", "Untitled")
        description = ticket.get("description", "")
        user = ticket.get("user", "Unknown")

        logger.info(f"🤖 LLM classifying ticket: {title}")

        # Build LLM prompt
        prompt = f"""Classify this IT support ticket into ONE category.

**Ticket Information**:
- ID: {ticket_id}
- Title: {title}
- Description: {description[:500]}
- User: {user}

**Available Categories**:
- network (WiFi, Ethernet, VPN, DNS, connectivity, internet issues)
- software (applications, updates, licenses, crashes, installations)
- hardware (devices, peripherals, screens, printers, disk issues)
- security (passwords, access, permissions, malware, unauthorized access)
- performance (slow computer, lag, freezing, high CPU/RAM)
- database (SQL errors, connection issues, data corruption)
- email (Outlook, SMTP, spam, attachments, email delivery)
- other (anything not fitting above categories)

**Instructions**:
Analyze the ticket and respond with ONLY the category name in lowercase.
Do not explain, just answer with one word.

Examples:
- "Cannot connect to WiFi" → network
- "Excel keeps crashing" → software
- "Forgot my password" → security

Category:"""

        start_time = datetime.now(timezone.utc)

        try:
            # Call Ollama LLM with automatic PRIMARY/BACKUP failover
            # Note: generate_with_fallback() has built-in timeout and retry logic
            result = await ollama_client.generate_with_fallback(
                prompt=prompt,
                agent_type="classifier"
            )

            # Log which Ollama server was used (for monitoring)
            ollama_source = result.get("source", "unknown")
            if ollama_source == "primary":
                logger.info(f"✅ Classification used PRIMARY Ollama (Corertx RTX 3060)")
            elif ollama_source == "fallback":
                logger.warning(f"⚠️ Classification used BACKUP Ollama (Edgeserver GTX 1050) - PRIMARY may be down")

            end_time = datetime.now(timezone.utc)
            processing_time_ms = int((end_time - start_time).total_seconds() * 1000)

            # Extract category from response
            category = result["response"].lower().strip()

            # Validate category
            if category not in VALID_TICKET_CATEGORIES:
                logger.warning(f"⚠️ LLM returned invalid category '{category}', using keywords fallback")
                return await self._classify_ticket_keywords(ticket)

            # Determine priority (use keywords for now, could be LLM too)
            priority = self._determine_priority_keywords(title, description)

            # Route to agent
            routed_to = self.routing_map.get(category, "ResolverAgent")

            self.classification_count += 1

            classification_result = {
                "status": "success",
                "ticket_id": ticket_id,
                "classification": {
                    "category": category,
                    "confidence": 0.90,  # LLM generally high confidence
                    "priority": priority,
                    "routed_to_agent": routed_to,
                    "method": "llm"
                },
                "analysis": {
                    "model": result["model"],
                    "tokens": result["tokens"],
                    "llm_duration_seconds": result["duration_seconds"]
                },
                "timestamp": end_time.isoformat(),
                "processing_time_ms": processing_time_ms
            }

            # Record metrics
            if LLM_AVAILABLE:
                record_classifier_llm(
                    duration=result["duration_seconds"],
                    category=category,
                    confidence=0.90,
                    tokens=result["tokens"]
                )

            logger.info(f"✅ LLM classified as {category} ({priority}) → {routed_to} in {processing_time_ms}ms")
            return classification_result

        except Exception as e:
            logger.error(f"❌ LLM classification error: {e}", exc_info=True)

            # Record error metric
            if LLM_AVAILABLE:
                classifier_llm_error.labels(error_type=type(e).__name__).inc()

            # Fallback to keyword classification
            logger.info("🔄 Falling back to keyword classification")
            return await self._classify_ticket_keywords(ticket)

    def _determine_priority_keywords(self, title: str, description: str) -> str:
        """Helper method to determine priority using keywords."""
        text = f"{title} {description}".lower()

        for level, keywords in self.priority_keywords.items():
            if any(keyword in text for keyword in keywords):
                return level

        return "medium"  # default

    async def _classify_ticket_keywords(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """
        FALLBACK: Classify a ticket using keyword analysis (original method).

        Analyzes title + description to determine:
        - Category (network, software, hardware, etc.)
        - Priority (critical, high, medium, low)
        - Routing (which agent should handle it)
        """
        logger.info(f"🔍 Keyword classifying ticket: {ticket.get('title', 'Untitled')}")

        start_time = time.time()

        ticket_id = ticket.get("id", f"T-{self.classification_count:04d}")
        title = ticket.get("title", "").lower()
        description = ticket.get("description", "").lower()
        text = f"{title} {description}"

        # Classify category
        category_scores = {}
        for category, keywords in self.categories.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score

        if category_scores:
            category = max(category_scores, key=category_scores.get)
            confidence = category_scores[category] / len(self.categories[category])
        else:
            category = "general"
            confidence = 0.0

        # Determine priority
        priority = "medium"  # default
        for level, keywords in self.priority_keywords.items():
            if any(keyword in text for keyword in keywords):
                priority = level
                break

        # Route to agent
        routed_to = self.routing_map.get(category, "ResolverAgent")

        # Extract keywords found
        found_keywords = []
        for keyword in self.categories.get(category, []):
            if keyword in text:
                found_keywords.append(keyword)

        self.classification_count += 1

        duration = time.time() - start_time

        result = {
            "status": "success",
            "ticket_id": ticket_id,
            "classification": {
                "category": category,
                "confidence": round(confidence, 2),
                "priority": priority,
                "routed_to_agent": routed_to,
                "method": "keywords"
            },
            "analysis": {
                "keywords_found": found_keywords[:5],  # Top 5
                "category_scores": category_scores,
                "text_length": len(text)
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "processing_time_ms": int(duration * 1000)
        }

        # Record metrics
        if LLM_AVAILABLE:
            record_classifier_fallback(
                duration=duration,
                category=category,
                confidence=confidence
            )

        logger.info(f"✅ Keyword classified as {category} ({priority}) → {routed_to}")
        return result

    async def _analyze_logs(self, logs: List[str]) -> Dict[str, Any]:
        """
        Analyze logs and auto-create tickets for errors.

        Parses log entries and detects:
        - Errors
        - Warnings
        - Crashes
        - Performance issues
        """
        logger.info(f"📋 Analyzing {len(logs)} log entries...")

        tickets_created = []
        errors_found = 0
        warnings_found = 0

        # Error patterns
        error_patterns = [
            (r"ERROR|CRITICAL|FATAL", "critical", "Application error detected"),
            (r"WARN|WARNING", "high", "Warning condition detected"),
            (r"Exception|Traceback|Stack trace", "high", "Exception occurred"),
            (r"timeout|timed out", "medium", "Timeout issue"),
            (r"connection refused|cannot connect", "high", "Connection failure")
        ]

        for log_entry in logs:
            for pattern, priority, description in error_patterns:
                if re.search(pattern, log_entry, re.IGNORECASE):
                    # Extract relevant info
                    timestamp_match = re.search(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}', log_entry)
                    timestamp = timestamp_match.group(0) if timestamp_match else "unknown"

                    ticket = {
                        "title": description,
                        "description": log_entry[:200],  # First 200 chars
                        "priority": priority,
                        "source": "log_analysis",
                        "timestamp": timestamp
                    }

                    # Classify the auto-generated ticket (use LLM if available)
                    if self.use_llm:
                        try:
                            classification = await self._classify_ticket_llm(ticket)
                        except Exception:
                            classification = await self._classify_ticket_keywords(ticket)
                    else:
                        classification = await self._classify_ticket_keywords(ticket)

                    tickets_created.append({
                        "ticket": ticket,
                        "classification": classification
                    })

                    if "ERROR" in pattern:
                        errors_found += 1
                    else:
                        warnings_found += 1

                    break  # Only one ticket per log line

        result = {
            "status": "success",
            "logs_analyzed": len(logs),
            "tickets_created": len(tickets_created),
            "errors_found": errors_found,
            "warnings_found": warnings_found,
            "tickets": tickets_created[:10],  # Return max 10
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"✅ Log analysis: {errors_found} errors, {warnings_found} warnings, {len(tickets_created)} tickets")
        return result

    async def _detect_patterns(self, tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect recurring patterns in tickets.

        Finds:
        - Common issues
        - Trending problems
        - Time-based patterns
        """
        logger.info(f"🔎 Detecting patterns in {len(tickets)} tickets...")

        # Count categories
        category_counts = {}
        priority_counts = {}

        for ticket in tickets:
            # Classify each ticket (use LLM if available)
            if self.use_llm:
                try:
                    classification = await self._classify_ticket_llm(ticket)
                except Exception:
                    classification = await self._classify_ticket_keywords(ticket)
            else:
                classification = await self._classify_ticket_keywords(ticket)

            category = classification["classification"]["category"]
            priority = classification["classification"]["priority"]

            category_counts[category] = category_counts.get(category, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        # Find trending issues
        trending = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)

        # Recommendations
        recommendations = []
        if category_counts.get("network", 0) > len(tickets) * 0.3:
            recommendations.append("High volume of network issues - investigate infrastructure")
        if priority_counts.get("critical", 0) > 5:
            recommendations.append("Multiple critical issues - escalate to senior team")

        result = {
            "status": "success",
            "tickets_analyzed": len(tickets),
            "patterns": {
                "by_category": category_counts,
                "by_priority": priority_counts,
                "trending_issues": dict(trending[:3])  # Top 3
            },
            "recommendations": recommendations,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"✅ Pattern detection complete: {len(trending)} categories found")
        return result
