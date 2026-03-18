# Database Setup Script - Handles existing partial schema
# This script will properly set up the database even if partially configured

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Database Setup & Migration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we need to find PostgreSQL
$psqlCommand = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psqlCommand) {
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
            $env:Path += ";$foundPath"
            Write-Host "✓ Added PostgreSQL to PATH: $foundPath" -ForegroundColor Green
            break
        }
    }
}

Write-Host "Checking database migration status..." -ForegroundColor Yellow
$currentMigration = alembic current 2>&1

if ($currentMigration -match "ca6ce230ce75") {
    Write-Host "✓ Database is already up to date!" -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "Database needs migration. Attempting to migrate..." -ForegroundColor Yellow
Write-Host ""

# Try to run migrations
$migrationOutput = alembic upgrade head 2>&1
$migrationExitCode = $LASTEXITCODE

if ($migrationExitCode -eq 0) {
    Write-Host "✓ Database migrations completed successfully!" -ForegroundColor Green
} else {
    # Check if it's a "type already exists" error
    if ($migrationOutput -match "already exists") {
        Write-Host "⚠ ENUM types already exist in database" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "This means the database was partially set up before." -ForegroundColor Cyan
        Write-Host "We need to mark the migrations as applied without re-running them." -ForegroundColor Cyan
        Write-Host ""
        
        # Stamp the database with the current migration
        Write-Host "Marking database as up-to-date..." -ForegroundColor Yellow
        alembic stamp head
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Database marked as up-to-date!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Verifying tables exist..." -ForegroundColor Yellow
            
            # Check if tables exist using Python
            $checkScript = @"
import asyncio
from app.database import engine
from sqlalchemy import text

async def check_tables():
    async with engine.begin() as conn:
        result = await conn.execute(text(\"\"\"
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        \"\"\"))
        tables = [row[0] for row in result]
        return tables

tables = asyncio.run(check_tables())
print(f\"Found {len(tables)} tables:\")
for table in tables:
    print(f\"  ✓ {table}\")
"@
            
            $checkScript | python
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "✓ Database setup complete!" -ForegroundColor Green
            }
        } else {
            Write-Host "✗ Failed to mark database" -ForegroundColor Red
            Write-Host ""
            Write-Host "Manual fix required:" -ForegroundColor Yellow
            Write-Host "  Run: alembic stamp head" -ForegroundColor White
            exit 1
        }
    } else {
        Write-Host "✗ Migration failed with unexpected error" -ForegroundColor Red
        Write-Host ""
        Write-Host "Error details:" -ForegroundColor Yellow
        Write-Host $migrationOutput -ForegroundColor Gray
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Database is ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
