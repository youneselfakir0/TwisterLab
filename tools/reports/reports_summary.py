import json
from pathlib import Path
from collections import defaultdict

repo_root = Path(__file__).resolve().parents[2]
report_dir = repo_root / 'tools' / 'reports'
inv_file = report_dir / 'docs_inventory.json'

with inv_file.open('r', encoding='utf-8') as fh:
    entries = json.load(fh)

count = len(entries)
print(f'Total doc/text files scanned: {count}')

# duplicates
hash_map = defaultdict(list)
for e in entries:
    if 'hash' in e:
        hash_map[e['hash']].append(e)

duplicates = {h: v for h, v in hash_map.items() if len(v) > 1}
print(f'Hashes with duplicates: {len(duplicates)}')

# top largest
sorted_by_size = sorted([e for e in entries if 'size' in e], key=lambda x: x['size'], reverse=True)
print('\nTop 10 largest docs:')
for e in sorted_by_size[:10]:
    print(f" - {e['path']} ({e['size']} bytes) - title: {e.get('title','')[:80]})")

# per-directory counts
dir_counts = defaultdict(int)
for e in entries:
    p = Path(e['path'])
    dir_counts[str(p.parent)] += 1

print('\nTop directories with most docs:')
for d, c in sorted(dir_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f' - {d}: {c} files')

# Show a sample of duplicates
print('\nSample duplicates:')
i = 0
for h, group in duplicates.items():
    print(f'Hash: {h} - {len(group)} files:')
    for g in group:
        print(f'  - {g["path"]}')
    i += 1
    if i >= 5:
        break
