# Start all 5 Zynd Agents for Fair Hiring Network
$env:PYTHONPATH = "D:\ZyndHiring\Zyndv1"
$VENV_PYTHON = "D:\ZyndHiring\Zyndv1\.venv\Scripts\python.exe"

Write-Host "Starting Zynd Agent Network..." -ForegroundColor Cyan

# Matching Agent
Write-Host "Starting Matching Agent on port 5101..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='D:\ZyndHiring\Zyndv1'; & '$VENV_PYTHON' -m zynd_integration.agents.matching_agent" -WindowStyle Normal

# Bias Agent
Write-Host "Starting Bias Agent on port 5102..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='D:\ZyndHiring\Zyndv1'; & '$VENV_PYTHON' -m zynd_integration.agents.bias_agent" -WindowStyle Normal

# Skill Agent
Write-Host "Starting Skill Agent on port 5103..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='D:\ZyndHiring\Zyndv1'; & '$VENV_PYTHON' -m zynd_integration.agents.skill_agent" -WindowStyle Normal

# ATS Agent
Write-Host "Starting ATS Agent on port 5104..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='D:\ZyndHiring\Zyndv1'; & '$VENV_PYTHON' -m zynd_integration.agents.ats_agent" -WindowStyle Normal

# Passport Agent
Write-Host "Starting Passport Agent on port 5105..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='D:\ZyndHiring\Zyndv1'; & '$VENV_PYTHON' -m zynd_integration.agents.passport_agent" -WindowStyle Normal

# GitHub Agent
Write-Host "Starting GitHub Agent on port 5106..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='D:\ZyndHiring\Zyndv1'; & '$VENV_PYTHON' -m zynd_integration.agents.github_agent" -WindowStyle Normal

# LinkedIn Agent
Write-Host "Starting LinkedIn Agent on port 5107..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='D:\ZyndHiring\Zyndv1'; & '$VENV_PYTHON' -m zynd_integration.agents.linkedin_agent" -WindowStyle Normal

Write-Host "All agents triggered. Please wait for them to initialize and register." -ForegroundColor Green
