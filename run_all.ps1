# Run pipeline + API + Dashboard in separate windows.
# Usage: .\run_all.ps1

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host "[1/4] Running pipeline (one-time)..."
python -m pipelines.daily_pipeline

Write-Host "[2/4] Starting FastAPI (uvicorn) in new window..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot'; uvicorn api.api_server:app --reload --host 127.0.0.1 --port 8000"

Write-Host "[3/4] Starting Streamlit dashboard in new window..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot'; streamlit run dashboard/streamlit_app.py"

Write-Host "All services started."
Write-Host "- API:    http://127.0.0.1:8000"
Write-Host "- Dashboard: http://localhost:8501"
