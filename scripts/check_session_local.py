import sys
sys.path.insert(0, r'C:\Users\Administrator\Documents\twisterlab\src')
import importlib, traceback

try:
    m = importlib.import_module('twisterlab.database.session')
    print('Have module', m)
    print('module file', m.__file__)
    names = [a for a in dir(m) if 'Session' in a or a == 'SessionLocal' or 'Async' in a]
    print('Names', names)
    print('SessionLocal', getattr(m, 'SessionLocal', None))
    print('AsyncSessionLocal', getattr(m, 'AsyncSessionLocal', None))
except Exception:
    traceback.print_exc()
    raise

import inspect
print('\nengine repr/dir:', getattr(m, 'engine', None))
e = getattr(m, 'engine', None)
if e is not None:
    print('engine class', type(e), 'attrs:', [a for a in dir(e) if not a.startswith('_')][:50])
    # Print the actual file content to see what code exists on disk
    print('\n=== FILE CONTENT START ===')
    with open(m.__file__, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, start=1):
            if i <= 80:
                print(f"{i:03d}: {line.rstrip()}")
            else:
                break
    print('=== FILE CONTENT END ===')
