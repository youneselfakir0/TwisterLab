import importlib, importlib.util, sys
sys.path.insert(0, r'C:\Users\Administrator\Documents\twisterlab\src')

import sys
for k in list(sys.modules.keys()):
    if k.startswith('twisterlab'):
        del sys.modules[k]

spec = importlib.util.find_spec('twisterlab.api.main')
print('spec', spec)
if spec is not None:
    print('origin', spec.origin)
    print('loader', type(spec.loader).__name__)
    with open(spec.origin, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, start=1):
            if i <= 30:
                print(f'{i:03d}: {line.rstrip()}')
            else:
                break
else:
    print('spec is None')
