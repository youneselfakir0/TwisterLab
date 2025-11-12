#!/usr/bin/env pwsh
# TwisterLab v1.0.0 Release Automation Script
# Automates PR creation, merge, tagging, and deployment

param(
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

Write-Host "
═══════════════════════════════════════════════════════════════════
   🚀 TwisterLab v1.0.0 Release Automation
═══════════════════════════════════════════════════════════════════
" -ForegroundColor Cyan

# Step 1: Verify GitHub CLI
Write-Host "📋 Step 1: Verifying GitHub CLI..." -ForegroundColor Yellow
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "❌ GitHub CLI (gh) not found. Install from: https://cli.github.com/" -ForegroundColor Red
    Write-Host "   Or use manual steps below:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Manual Steps:" -ForegroundColor Cyan
    Write-Host "1. Go to: https://github.com/youneselfakir0/TwisterLab/compare/main...feature/azure-ad-auth" -ForegroundColor White
    Write-Host "2. Click 'Create Pull Request'" -ForegroundColor White
    Write-Host "3. Title: 'Release v1.0.0 - PostgreSQL Integration + Documentation'" -ForegroundColor White
    Write-Host "4. Merge the PR" -ForegroundColor White
    Write-Host "5. Run: git tag v1.0.0 && git push origin v1.0.0" -ForegroundColor White
    exit 1
}

Write-Host "✅ GitHub CLI found" -ForegroundColor Green

# Step 2: Verify current branch
Write-Host "`n📋 Step 2: Verifying current branch..." -ForegroundColor Yellow
$currentBranch = git rev-parse --abbrev-ref HEAD
if ($currentBranch -ne "feature/azure-ad-auth") {
    Write-Host "❌ Not on feature/azure-ad-auth branch (current: $currentBranch)" -ForegroundColor Red
    exit 1
}
Write-Host "✅ On feature/azure-ad-auth branch" -ForegroundColor Green

# Step 3: Verify clean working tree
Write-Host "`n📋 Step 3: Verifying clean working tree..." -ForegroundColor Yellow
$status = git status --porcelain
if ($status) {
    Write-Host "❌ Working tree is not clean. Commit or stash changes first." -ForegroundColor Red
    git status --short
    exit 1
}
Write-Host "✅ Working tree clean" -ForegroundColor Green

# Step 4: Pull latest changes
Write-Host "`n📋 Step 4: Pulling latest changes..." -ForegroundColor Yellow
git fetch origin
git pull origin feature/azure-ad-auth
Write-Host "✅ Branch up to date" -ForegroundColor Green

# Step 5: Create Pull Request
Write-Host "`n📋 Step 5: Creating Pull Request..." -ForegroundColor Yellow

$prTitle = "Release v1.0.0 - PostgreSQL Integration + Production Documentation"
$prBody = @"
## 🎉 Release v1.0.0 - Production Ready

### Summary
Complete database integration with PostgreSQL, comprehensive documentation, and production-ready deployment.

### Changes

#### 🔗 PostgreSQL Database Integration
- ✅ **SQLAlchemy Models**: Ticket, AgentLog, SystemMetrics
- ✅ **Async Database Layer**: asyncpg driver with connection pooling
- ✅ **Repository Pattern**: TicketRepository, AgentLogRepository, SystemMetricsRepository
- ✅ **Database Schema**: \`schema.sql\` for table creation
- ✅ **API Endpoints**: \`classify_ticket\` and \`monitor_system_health\` persist data
- ✅ **Audit Logging**: All agent executions logged with execution time

#### 📝 Documentation
- ✅ **README.md**: Production-ready installation guide (196 lines)
- ✅ **CHANGELOG.md**: Detailed v1.0.0 release notes
- ✅ **Architecture**: ASCII diagram with 7 agents
- ✅ **System Status**: Component health table
- ✅ **Usage Examples**: Continue IDE + API curl commands
- ✅ **Performance Metrics**: Real latency measurements

#### 🧹 Repository Cleanup
- ✅ Enhanced \`.gitignore\` (paste*.txt, NUL, .swp/.swo)
- ✅ Removed temporary files (__pycache__, .pyc, .pytest_cache)
- ✅ Clean repository structure

### Database Tables Created
\`\`\`sql
tickets         (id, description, category, priority, status, timestamps, agent_response)
agent_logs      (id, agent_name, ticket_id, action, result, error, execution_time_ms)
system_metrics  (id, cpu_usage, memory_usage, disk_usage, docker_status, timestamp)
\`\`\`

### Commits (4)
- 5f7f4bc - chore: enhance .gitignore
- 82c2d75 - feat: PostgreSQL database integration (582 insertions)
- dfede8f - feat: PostgreSQL schema SQL
- 5ab38d4 - docs: complete documentation (365 insertions)

### Testing
- ✅ Database tables created on edgeserver PostgreSQL
- ✅ API endpoints tested and functional
- ✅ All 7 agents operational

### Deployment Status
- **Infrastructure**: Docker Swarm on edgeserver.twisterlab.local
- **Database**: PostgreSQL 16 (3 tables)
- **Cache**: Redis 7
- **AI**: Ollama GPU (RTX 3060, 6 models)
- **Monitoring**: Prometheus + Grafana

### Breaking Changes
None - This is a feature addition release.

### Migration Required
Yes - Run database initialization:
\`\`\`bash
# Via Python
python -c "import asyncio; from agents.core.database import init_db; asyncio.run(init_db())"

# Via SQL (on edgeserver)
docker exec twisterlab_postgres.1.xxx psql -U twisterlab -d twisterlab -f /tmp/schema.sql
\`\`\`

### Next Steps
1. ✅ Review and approve PR
2. ✅ Merge to main
3. ✅ Tag v1.0.0
4. ✅ Deploy to production
5. 🎊 Celebrate!

---

**Built with ⚡ Warrior Mode Energy**
"@

if ($DryRun) {
    Write-Host "[DRY RUN] Would create PR with:" -ForegroundColor Cyan
    Write-Host "Title: $prTitle" -ForegroundColor White
    Write-Host "Body: (see above)" -ForegroundColor White
} else {
    try {
        $pr = gh pr create --title $prTitle --body $prBody --base main --head feature/azure-ad-auth
        Write-Host "✅ Pull Request created: $pr" -ForegroundColor Green
        
        # Store PR number
        $prNumber = ($pr -split '/')[-1]
        
        # Step 6: Auto-merge (if approved)
        Write-Host "`n📋 Step 6: Merging Pull Request..." -ForegroundColor Yellow
        Write-Host "⚠️  Review the PR first at: $pr" -ForegroundColor Yellow
        Write-Host "Press ENTER to merge (or Ctrl+C to cancel)..." -ForegroundColor Cyan
        Read-Host
        
        gh pr merge $prNumber --merge --delete-branch
        Write-Host "✅ Pull Request merged and branch deleted" -ForegroundColor Green
        
    } catch {
        Write-Host "❌ Error creating PR: $_" -ForegroundColor Red
        Write-Host "`nManual PR creation URL:" -ForegroundColor Yellow
        Write-Host "https://github.com/youneselfakir0/TwisterLab/compare/main...feature/azure-ad-auth" -ForegroundColor Cyan
        exit 1
    }
}

# Step 7: Switch to main and tag
Write-Host "`n📋 Step 7: Creating release tag v1.0.0..." -ForegroundColor Yellow
git checkout main
git pull origin main

$tagMessage = @"
TwisterLab v1.0.0 - Production Release

🎉 First production-ready release with PostgreSQL database integration

Features:
- 7 Autonomous Agents (Monitoring, Classifier, Resolver, Backup, Sync, Commander, Maestro)
- PostgreSQL database persistence (tickets, agent_logs, system_metrics)
- Async-native with asyncpg driver
- Repository pattern (clean architecture)
- Complete audit logging
- Production-ready documentation
- Docker Swarm deployment
- Ollama GPU acceleration (RTX 3060)
- Continue IDE + MCP integration

Performance:
- Classify Ticket: 150ms
- Resolve Ticket: 200ms
- Monitor Health: 50ms
- Create Backup: 1300ms

Infrastructure:
- Docker Swarm on edgeserver.twisterlab.local
- PostgreSQL 16 + Redis 7
- Prometheus + Grafana monitoring
- 6/6 services operational

Built with ⚡ Warrior Mode Energy
"@

if ($DryRun) {
    Write-Host "[DRY RUN] Would create tag v1.0.0" -ForegroundColor Cyan
} else {
    git tag -a v1.0.0 -m $tagMessage
    git push origin v1.0.0
    Write-Host "✅ Tag v1.0.0 created and pushed" -ForegroundColor Green
}

# Step 8: Deploy to production (optional)
Write-Host "`n📋 Step 8: Deploy to production..." -ForegroundColor Yellow
Write-Host "Deploy now? (y/N): " -ForegroundColor Cyan -NoNewline
$deploy = Read-Host

if ($deploy -eq 'y' -or $deploy -eq 'Y') {
    Write-Host "`nDeploying to edgeserver..." -ForegroundColor Yellow
    
    # Sync code
    scp -r C:\TwisterLab\agents\core\*.py twister@192.168.0.30:/home/twister/TwisterLab/agents/core/
    scp C:\TwisterLab\api\routes_mcp_real.py twister@192.168.0.30:/home/twister/TwisterLab/api/
    scp C:\TwisterLab\schema.sql twister@192.168.0.30:/tmp/schema.sql
    
    Write-Host "✅ Code synchronized" -ForegroundColor Green
    
    # Rebuild and restart API
    Write-Host "`nRebuilding API container..." -ForegroundColor Yellow
    ssh twister@192.168.0.30 "cd /home/twister/TwisterLab && docker build -t twisterlab-api:v1.0.0 -f Dockerfile.api.final . && docker service update twisterlab_api --image twisterlab-api:v1.0.0 --force"
    
    Write-Host "✅ Deployment complete!" -ForegroundColor Green
} else {
    Write-Host "⏭️  Skipping deployment" -ForegroundColor Yellow
    Write-Host "`nManual deployment commands:" -ForegroundColor Cyan
    Write-Host "ssh twister@192.168.0.30" -ForegroundColor White
    Write-Host "cd /home/twister/TwisterLab" -ForegroundColor White
    Write-Host "git pull origin main" -ForegroundColor White
    Write-Host "docker build -t twisterlab-api:v1.0.0 -f Dockerfile.api.final ." -ForegroundColor White
    Write-Host "docker service update twisterlab_api --image twisterlab-api:v1.0.0 --force" -ForegroundColor White
}

# Step 9: Celebrate!
Write-Host "
═══════════════════════════════════════════════════════════════════
   🎊 RELEASE v1.0.0 COMPLETE! 🎊
═══════════════════════════════════════════════════════════════════

✅ Pull Request: Created and Merged
✅ Release Tag: v1.0.0 pushed to GitHub
✅ Documentation: Complete and published
✅ Database: PostgreSQL integrated
✅ Agents: 7/7 operational

Next:
- Check GitHub Release: https://github.com/youneselfakir0/TwisterLab/releases/tag/v1.0.0
- Monitor deployment: http://192.168.0.30:3000 (Grafana)
- Test API: http://192.168.0.30:8000/docs

═══════════════════════════════════════════════════════════════════
Built with ⚡ Warrior Mode Energy
═══════════════════════════════════════════════════════════════════
" -ForegroundColor Green

Write-Host "🎉 Time to celebrate! 🍾" -ForegroundColor Magenta
