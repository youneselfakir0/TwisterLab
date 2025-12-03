from twisterlab.agents.mcp.mcp_server import MCPServerContinue
server = MCPServerContinue()
print('✅ Server initialized successfully')
print(f'Mode: {server.mode}')
print(f'API Available: {server.api_available}')
print(f'Protocol: {server.protocol_version}')
print(f'Server: {server.server_info["name"]} v{server.server_info["version"]}')