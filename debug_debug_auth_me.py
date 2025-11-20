from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from api.main import app

client = TestClient(app)

mock_user = {"sub": "user-123", "name": "Test User", "preferred_username": "test@example.com", "roles": ["user", "admin"], "tid": "tenant-123"}

with patch('api.auth.verify_jwt_token', new_callable=AsyncMock) as mock_verify:
    mock_verify.return_value = mock_user
    response = client.get('/auth/me', headers={'Authorization': 'Bearer mock_valid_token'})
    print('status_code =', response.status_code)
    print('headers =', response.headers)
    try:
        print('json =', response.json())
    except Exception as e:
        print('json parse error:', e)
