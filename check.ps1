$ErrorActionPreference = "Stop"
$python = ".\.venv\Scripts\python.exe"
& $python -m black --check .
if ($LASTEXITCODE -ne 0) { exit 1 }
& $python -m ruff check .
if ($LASTEXITCODE -ne 0) { exit 1 }
& $python -m pytest -q
if ($LASTEXITCODE -ne 0) { exit 1 }
