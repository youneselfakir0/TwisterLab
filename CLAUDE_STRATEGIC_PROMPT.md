# CLAUDE STRATEGIC PLANNING PROMPT

You are Claude, the strategic AI architect for TwisterLab.

## CONTEXT
- Project: TwisterLab v1.0.0 (Autonomous AI IT Helpdesk)
- Status: Core infrastructure complete, ClassifierAgent implemented
- Remaining: 6 AI agents to implement
- Framework: Async Python, FastAPI, SQLAlchemy, Redis

## TASK: Generate Implementation Roadmap for 6 Remaining Agents

### Available Template (Reference)
ClassifierAgent shows the pattern:
- Multi-strategy processing
- Confidence scoring
- Escalation logic
- Inter-agent communication
- Health monitoring

### REQUIRED AGENTS (in order of dependency)

1. **ResolverAgent** (PRIORITY 1)
   - Dependencies: Receives from ClassifierAgent
   - Function: Execute troubleshooting SOPs
   - Output: Solution + execution logs
   
2. **Desktop-CommanderAgent** (PRIORITY 2)
   - Dependencies: Called by Resolver for system commands
   - Function: Safe remote execution
   - Output: Command results + audit trail

3. **MaestroOrchestratorAgent** (PRIORITY 3)
   - Dependencies: Coordinates all agents
   - Function: Load balancing + escalation
   - Output: Orchestration decisions

4. **Sync-AgentAgent** (PRIORITY 4)
   - Dependencies: Called by Maestro
   - Function: Data consistency
   - Output: Sync status

5. **Backup-AgentAgent** (PRIORITY 5)
   - Dependencies: Scheduled by Maestro
   - Function: Data protection
   - Output: Backup status

6. **Monitoring-AgentAgent** (PRIORITY 6)
   - Dependencies: Continuous monitoring
   - Function: Metrics collection
   - Output: Performance data

## YOUR TASK

For EACH agent, provide:

1. **Architecture Overview**
   - Role in system
   - Input/output format
   - Decision logic

2. **Code Template**
   - Class structure (inherit from BaseAgent)
   - Key methods to implement
   - Error handling pattern
   - Logging strategy

3. **Integration Points**
   - How to communicate with other agents
   - Email routing setup
   - API endpoints needed
   - Database queries

4. **Testing Strategy**
   - Unit test patterns
   - Integration test scenarios
   - Mock data needed

5. **Deployment Notes**
   - Configuration needed
   - Environment variables
   - Docker setup
   - Monitoring setup

## CONSTRAINTS
- Follow patterns from ClassifierAgent (see agents/helpdesk/classifier.py)
- Use TwisterAgent base class pattern (see agents/base.py)
- Async/await throughout
- Proper error handling
- Comprehensive logging
- Type hints on all functions
- Maximum 5 MCP tools per agent
- Single-purpose agents (no multi-domain)

## REFERENCE FILES IN PROJECT

Key files to reference:
- `agents/base.py` - TwisterAgent base class
- `agents/helpdesk/classifier.py` - Complete ClassifierAgent implementation (750+ lines)
- `agents/orchestrator/maestro.py` - Existing Maestro stub
- `.github/copilot-instructions.md` - Project conventions
- `AI_CODING_INSTRUCTIONS_v5_FINAL.md` - Detailed patterns (if available)

## OUTPUT FORMAT

For each agent, provide structured markdown with:
- Clear section headers
- Complete code blocks
- Integration examples
- Test examples
- Configuration snippets

Focus on being detailed and actionable - Copilot will implement based on your specifications.

---

**GENERATE THE COMPLETE IMPLEMENTATION ROADMAP FOR ALL 6 AGENTS**
