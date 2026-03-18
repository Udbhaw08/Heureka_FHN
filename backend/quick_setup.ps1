# Quick Setup Script for Fair Hiring Backend
# Run this script to set up the backend environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fair Hiring Backend - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check PostgreSQL
Write-Host "[Step 1/5] Checking PostgreSQL..." -ForegroundColor Yellow

# Check if psql is available
$psqlCommand = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psqlCommand) {
    Write-Host "⚠ psql command not found in PATH" -ForegroundColor Yellow
    Write-Host "  pgAdmin 4 is running, but we need to add PostgreSQL bin to PATH" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Common PostgreSQL bin locations:" -ForegroundColor White
    Write-Host "  - C:\Program Files\PostgreSQL\14\bin" -ForegroundColor Gray
    Write-Host "  - C:\Program Files\PostgreSQL\15\bin" -ForegroundColor Gray
    Write-Host "  - C:\Program Files\PostgreSQL\16\bin" -ForegroundColor Gray
    Write-Host ""
    
    # Try to find PostgreSQL installation
    $pgPaths = @(
        "C:\Program Files\PostgreSQL\16\bin",
        "C:\Program Files\PostgreSQL\15\bin",
        "C:\Program Files\PostgreSQL\14\bin",
        "C:\Program Files\PostgreSQL\13\bin"
    )
    
    $foundPath = $null
    foreach ($path in $pgPaths) {
        if (Test-Path "$path\psql.exe") {
            $foundPath = $path
            break
        }
    }
    
    if ($foundPath) {
        Write-Host "✓ Found PostgreSQL at: $foundPath" -ForegroundColor Green
        Write-Host "  Adding to PATH for this session..." -ForegroundColor Cyan
        $env:Path += ";$foundPath"
        Write-Host "✓ PostgreSQL added to PATH" -ForegroundColor Green
    } else {
        Write-Host "✗ Could not find PostgreSQL installation" -ForegroundColor Red
        Write-Host ""
        Write-Host "  Manual fix: Add PostgreSQL bin directory to your PATH" -ForegroundColor Yellow
        Write-Host "  Then run this script again" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Skipping database check and continuing setup..." -ForegroundColor Cyan
        Write-Host "  You can verify database connection manually later" -ForegroundColor Cyan
        Write-Host ""
    }
} else {
    # psql is available, test connection
    try {
        $dbCheck = psql -U postgres -d Udbhaw_Db -c "SELECT 1;" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Database 'Udbhaw_Db' is accessible" -ForegroundColor Green
        } else {
            Write-Host "⚠ Cannot connect to database 'Udbhaw_Db'" -ForegroundColor Yellow
            Write-Host "  This is OK - database might not exist yet" -ForegroundColor Cyan
            Write-Host "  Migrations will handle table creation" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "⚠ Could not test database connection" -ForegroundColor Yellow
        Write-Host "  Continuing with setup..." -ForegroundColor Cyan
    }
}

# Step 2: Check Python
Write-Host ""
Write-Host "[Step 2/5] Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found" -ForegroundColor Red
    exit 1
}

# Step 3: Create/Activate Virtual Environment
Write-Host ""
Write-Host "[Step 3/5] Setting up virtual environment..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Step 4: Install Dependencies
Write-Host ""
Write-Host "[Step 4/5] Installing dependencies..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor Cyan
.\venv\Scripts\activate
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Step 5: Run Database Migrations
Write-Host ""
Write-Host "[Step 5/5] Running database migrations..." -ForegroundColor Yellow
alembic upgrade head
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Database migrations completed" -ForegroundColor Green
} else {
    Write-Host "✗ Database migrations failed" -ForegroundColor Red
    exit 1
}

# Success Message
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Start the backend server:" -ForegroundColor White
Write-Host "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Start agent services (in a separate terminal):" -ForegroundColor White
Write-Host "   cd ..\agents_services" -ForegroundColor Yellow
Write-Host "   python start_all_complete.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Access API documentation:" -ForegroundColor White
Write-Host "   http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
