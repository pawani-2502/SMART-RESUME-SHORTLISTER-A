# Start the live Resume Shortlister stack (local dev)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Host "Creating virtual environment..."
    & "C:\Users\Kumar\AppData\Local\Programs\Python\Python311\python.exe" -m venv .venv
    & ".\.venv\Scripts\pip.exe" install -r backend\requirements.txt
}

Write-Host "Starting backend on http://localhost:8000 ..."
$env:PYTHONPATH = $Root
Start-Process -FilePath $Python -ArgumentList "-m","uvicorn","backend.main:app","--host","0.0.0.0","--port","8000","--reload" -WorkingDirectory $Root -WindowStyle Normal

Write-Host "Starting frontend on http://localhost:3000 ..."
Start-Process -FilePath "npm" -ArgumentList "run","dev" -WorkingDirectory (Join-Path $Root "frontend") -WindowStyle Normal

Write-Host ""
Write-Host "Live app starting:"
Write-Host "  Frontend: http://localhost:3000"
Write-Host "  Backend:  http://localhost:8000/docs"
Write-Host "  Login:    admin@shortlister.ai / admin123"
Write-Host "  Demo:     http://localhost:3000/demo?mode=examiner"
