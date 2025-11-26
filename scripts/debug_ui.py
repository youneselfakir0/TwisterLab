from twisterlab.api.main import STATIC_UI
from pathlib import Path
print('STATIC_UI path ->', STATIC_UI)
print('exists ->', Path(STATIC_UI).exists())
print('files ->', list(Path(STATIC_UI).iterdir())[:5])
