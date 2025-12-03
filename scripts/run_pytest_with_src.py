import sys
sys.path.insert(0, r'C:\Users\Administrator\Documents\twisterlab\src')
import pytest
import os

# print sys.path for debugging
print('sys.path[0]:', sys.path[0])
res = pytest.main(['-q'])
print('pytest exit code', res)
sys.exit(res)
