# TwisterLab MCP + Copilot Integration

## 🚀 Quick Start

This `.copilot/` directory contains the complete MCP (Model Context Protocol) + GitHub Copilot integration for TwisterLab orchestration.

### Prerequisites
- VS Code with GitHub Copilot extension
- MCP extension installed (`@model-context-protocol`)
- GitHub repository access (youneselfakir0/twisterlab)
- Azure subscription (trial/credits)
- Grafana instance (optional for Phase 2+)

### Setup
1. Open the `twisterlab` repository in VS Code
2. Install MCP extension if not already installed
3. Configure MCP servers (see `mcp_config.json`)
4. Test with: `@twisterlab status`

### Available Commands
- `@twisterlab status` - Check system readiness
- `@twisterlab Execute Phase 0` - Pre-flight validation
- `@twisterlab Execute Phase 1` - GitHub deployment
- `@twisterlab Execute Phase 2` - Grafana setup
- `@twisterlab Execute Phase 3` - Autonomous operations
- `@twisterlab Execute Phase 4` - Community release
- `@twisterlab metrics` - Show real-time metrics
- `@twisterlab costs` - Show Azure spending
- `@twisterlab help` - Show this help

## 📁 Directory Structure

```
.copilot/
├── README.md              # This file
├── system_prompt.md       # Main Copilot system prompt
├── mcp_config.json        # MCP server configuration
├── mcp_commands.yaml      # Complete command library
└── workflows/
    ├── phase_0_preflight.yaml
    ├── phase_1_deployment.yaml
    ├── phase_2_grafana.yaml
    ├── phase_3_autonomous.yaml
    └── phase_4_community.yaml
```

## 🔧 MCP Server Configuration

The system uses 4 MCP servers:

### 1. GitHub MCP Server
- **Purpose**: Repository management, commits, PRs, releases
- **Auth**: GitHub Personal Access Token (PAT)
- **Scope**: `repo`, `workflow`, `write:packages`

### 2. Azure MCP Server
- **Purpose**: Infrastructure provisioning, resource management
- **Auth**: Azure Service Principal
- **Permissions**: Contributor role on subscription

### 3. Local MCP Server
- **Purpose**: Run tests, builds, linting, security scanning
- **Endpoint**: `localhost:3000`
- **Requirements**: Python 3.8+, Node.js (for some tools)

### 4. Grafana MCP Server
- **Purpose**: Dashboard management, alerting, metrics
- **Auth**: Grafana API key
- **Permissions**: Admin or Editor role

## 🚀 Phase Execution Workflow

Each phase follows this pattern:

1. **Trigger**: `@twisterlab Execute Phase [N]`
2. **Load**: Copilot loads system prompt + phase workflow
3. **Execute**: MCP commands run in sequence
4. **Interact**: Human approval for critical steps (PRs, deployments)
5. **Report**: Real-time status updates in VS Code
6. **Complete**: Phase completion confirmation

## 📊 Real-Time Monitoring

- **Metrics**: `@twisterlab metrics` shows live dashboards
- **Costs**: `@twisterlab costs` shows Azure spending
- **Status**: `@twisterlab status` shows system health
- **Logs**: All MCP commands logged in VS Code terminal

## 🛠️ Troubleshooting

### MCP Server Connection Issues
```bash
# Test MCP servers
@mcp github list-repo-files youneselfakir0/twisterlab
@mcp azure verify-credentials
@mcp local run-tests --help
@mcp grafana ping
```

### Copilot Not Responding
- Ensure Copilot extension is enabled
- Check that `.copilot/system_prompt.md` is accessible
- Try restarting VS Code
- Verify repository is open in workspace

### Authentication Errors
- GitHub: Regenerate PAT with correct scopes
- Azure: Verify service principal credentials
- Grafana: Check API key permissions

## 📚 Documentation

- **[MCP Integration Guide](../docs/MCP_INTEGRATION.md)** - Complete setup guide
- **[TwisterLang Guide](../docs/TWISTERLANG_GUIDE.md)** - Protocol specification
- **[API Reference](../docs/API_REFERENCE.md)** - All functions and endpoints
- **[Troubleshooting](../docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🤝 Contributing

To extend the MCP integration:

1. Add new MCP commands to `mcp_commands.yaml`
2. Update workflows in `workflows/` directory
3. Test with `@twisterlab status`
4. Submit PR with documentation updates

## 📞 Support

- **GitHub Issues**: [Report bugs](https://github.com/youneselfakir0/twisterlab/issues)
- **Discussions**: [Community Q&A](https://github.com/youneselfakir0/twisterlab/discussions)
- **Email**: youneselfakir@outlook.com

---

**Ready to orchestrate TwisterLab?** `@twisterlab Execute Phase 0` 🚀