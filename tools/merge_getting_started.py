"""
Simple merge tool to create a draft Getting Started doc by concatenating files from archive/docs/GETTING_STARTED.
This is a mechanical merge to create a reviewable draft; manual edits are expected after.
"""
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
archive_dir = repo_root / 'archive' / 'docs' / 'GETTING_STARTED'
out_file = repo_root / 'docs' / 'GETTING_STARTED_draft.md'

if not archive_dir.exists():
    print(f'Archive GETTING_STARTED dir not found: {archive_dir}'); exit(1)

parts = sorted(list(archive_dir.glob('*.md')))

with out_file.open('w', encoding='utf-8') as out:
    out.write('# Getting Started (Draft) - Consolidated from archive\n\n')
    out.write('This is a mechanical draft combining several archived quick-start files. Please review and edit to produce the final `docs/GETTING_STARTED.md`.\n\n')
    for p in parts:
        out.write(f'---\n\n## Source: {p.name}\n\n')
        content = p.read_text(encoding='utf-8')
        out.write(content)
        out.write('\n\n')

print(f'Wrote consolidated draft to {out_file}')
