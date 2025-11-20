from api.main import app
routes = [r.path for r in app.router.routes]
print([p for p in routes if '/v1/mcp' in p or 'mcp' in p])
