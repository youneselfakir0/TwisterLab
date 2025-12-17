import sys
sys.path.insert(0, r'C:\Users\Administrator\Documents\twisterlab\src')

from twisterlab.api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print(f'API Version: {app.version}')

# Get OpenAPI schema
r = client.get('/openapi.json')
paths = r.json()['paths']
mcp_paths = [p for p in paths.keys() if 'mcp' in p.lower() or 'sentiment' in p.lower()]

print(f'\nMCP/Sentiment paths found: {len(mcp_paths)}')
for p in mcp_paths[:10]:
    print(f'  {p}')

# Test analyze_sentiment
test_req = {'text': 'Fantastic product!', 'detailed': True}
r2 = client.post('/api/v1/mcp/analyze_sentiment', json=test_req)

print(f'\nTest /api/v1/mcp/analyze_sentiment:')
print(f'  Status: {r2.status_code}')
if r2.status_code == 200:
    print(f'  Response: {r2.json()}')
else:
    print(f'  Error: {r2.text}')
