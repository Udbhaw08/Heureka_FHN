# Start Frontend Dev Server
Set-Location "D:\ZyndHiring\Zyndv1\fair-hiring-frontend"

Write-Host "Starting Frontend on port 5173..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev" -WindowStyle Normal

Write-Host "Frontend triggered." -ForegroundColor Green
