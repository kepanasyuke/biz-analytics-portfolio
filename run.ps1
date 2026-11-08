param([switch]$SkipBuild)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$nodeDir = Join-Path $root ".tools\node-v26.13.0-win-x64"
$env:PATH = "$nodeDir;$env:PATH"

$apps = @(
  @{ Name = "sales-pulse"; Port = 8001; Title = "Sales Pulse" },
  @{ Name = "stockroom"; Port = 8002; Title = "Stockroom" },
  @{ Name = "finboard"; Port = 8003; Title = "FinBoard" },
  @{ Name = "crm-funnel"; Port = 8004; Title = "CRM Funnel" },
  @{ Name = "churn-radar"; Port = 8005; Title = "Churn Radar" },
  @{ Name = "pricing-lab"; Port = 8006; Title = "Pricing Lab" }
)

if (-not $SkipBuild) {
  Write-Host "Собираю фронтенды..." -ForegroundColor Cyan
  & npm run build --prefix $root
}

foreach ($app in $apps) {
  $backend = Join-Path $root "apps\$($app.Name)\backend"
  $args = @("-m", "uvicorn", "app.main:app", "--app-dir", $backend, "--port", $app.Port, "--host", "127.0.0.1")
  Start-Process -FilePath $python -ArgumentList $args -WindowStyle Hidden
  Write-Host ("  {0,-14} http://127.0.0.1:{1}" -f $app.Title, $app.Port) -ForegroundColor Green
}

Write-Host "`nВсе сервисы запущены. Остановить: Get-Process python | Stop-Process" -ForegroundColor Yellow
