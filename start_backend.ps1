# Start Backend API
$PROJECT_ROOT = $PSScriptRoot
$env:PYTHONPATH = "$PROJECT_ROOT\backend"
$VENV_PYTHON = "$PROJECT_ROOT\.venv\Scripts\python.exe"

Write-Host "Starting Backend API on port 8010..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='$PROJECT_ROOT\backend'; & '$VENV_PYTHON' -m uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload" -WindowStyle Normal -WorkingDirectory "$PROJECT_ROOT\backend"

Write-Host "Backend API triggered." -ForegroundColor Green
