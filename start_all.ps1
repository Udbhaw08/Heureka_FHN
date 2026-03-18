$PROJECT_ROOT = $PSScriptRoot
Set-Location $PROJECT_ROOT

$PYTHON_EXE = "$PROJECT_ROOT\.venv\Scripts\python.exe"
if (!(Test-Path $PYTHON_EXE)) {
    $PYTHON_EXE = "python"
}

$env:PYTHONPATH="$PROJECT_ROOT\backend;$PROJECT_ROOT"
$env:ZYND_REGISTRY_URL="https://registry.zynd.ai"
$env:ZYND_WEBHOOK_HOST="127.0.0.1"
$env:USE_ZYND="1"

$ports = 5100, 5101, 5102, 5103, 5104, 5105, 5106, 5107
foreach ($port in $ports) {
    Write-Host "Checking port $port..."
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($conns) {
        foreach ($conn in $conns) {
            $proc_id = $conn.OwningProcess
            if ($proc_id -gt 0) {
                Write-Host "Killing process $proc_id on port $port"
                Stop-Process -Id $proc_id -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

Write-Host "🧹 Resetting agent state to avoid unauthorized errors..." -ForegroundColor Yellow
& $PYTHON_EXE reset_for_demo.py

Start-Sleep -s 3

Write-Host "Starting Backend (API on 8012, Registry on 5100)..."
Start-Process $PYTHON_EXE -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8012 --log-level info" -NoNewWindow -WorkingDirectory "$PROJECT_ROOT\backend" -RedirectStandardOutput "backend.log" -RedirectStandardError "backend_err.log"
Start-Sleep -s 10

Write-Host "Starting Matching Agent (5101)..."
Start-Process $PYTHON_EXE -ArgumentList "-m zynd_integration.agents.matching_agent" -NoNewWindow -WorkingDirectory $PROJECT_ROOT -RedirectStandardOutput "matching_agent.log" -RedirectStandardError "matching_agent_err.log"
Start-Sleep -s 2

Write-Host "Starting Bias Agent (5102)..."
Start-Process $PYTHON_EXE -ArgumentList "-m zynd_integration.agents.bias_agent" -NoNewWindow -WorkingDirectory $PROJECT_ROOT -RedirectStandardOutput "bias_agent.log" -RedirectStandardError "bias_agent_err.log"
Start-Sleep -s 2

Write-Host "Starting Skill Agent (5103)..."
Start-Process $PYTHON_EXE -ArgumentList "-m zynd_integration.agents.skill_agent" -NoNewWindow -WorkingDirectory $PROJECT_ROOT -RedirectStandardOutput "skill_agent.log" -RedirectStandardError "skill_agent_err.log"
Start-Sleep -s 2

Write-Host "Starting ATS Agent (5104)..."
Start-Process $PYTHON_EXE -ArgumentList "-m zynd_integration.agents.ats_agent" -NoNewWindow -WorkingDirectory $PROJECT_ROOT -RedirectStandardOutput "ats_agent.log" -RedirectStandardError "ats_agent_err.log"
Start-Sleep -s 2

Write-Host "Starting Passport Agent (5105)..."
Start-Process $PYTHON_EXE -ArgumentList "-m zynd_integration.agents.passport_agent" -NoNewWindow -WorkingDirectory $PROJECT_ROOT -RedirectStandardOutput "passport_agent.log" -RedirectStandardError "passport_agent_err.log"
Start-Sleep -s 2

Write-Host "Starting GitHub Agent (5106)..."
Start-Process $PYTHON_EXE -ArgumentList "-m zynd_integration.agents.github_agent" -NoNewWindow -WorkingDirectory $PROJECT_ROOT -RedirectStandardOutput "github_agent.log" -RedirectStandardError "github_agent_err.log"
Start-Sleep -s 2

Write-Host "Starting LinkedIn Agent (5107)..."
Start-Process $PYTHON_EXE -ArgumentList "-m zynd_integration.agents.linkedin_agent" -NoNewWindow -WorkingDirectory $PROJECT_ROOT -RedirectStandardOutput "linkedin_agent.log" -RedirectStandardError "linkedin_agent_err.log"

Write-Host "System initialized on 127.0.0.1. Checking ports in 5 seconds..."
Start-Sleep -s 5
Get-NetTCPConnection -LocalPort $ports -State Listen -ErrorAction SilentlyContinue | Select-Object LocalPort, OwningProcess
