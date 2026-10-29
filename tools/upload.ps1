param([Parameter(Mandatory=$true)][string]$Port)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
$firmwarePath = Join-Path $projectRoot 'firmware'
if (-not (Test-Path -LiteralPath (Join-Path $firmwarePath 'config_local.py'))) {
    throw 'Crear firmware/config_local.py con la configuración del montaje antes de cargar.'
}
Write-Host 'Cargar únicamente con la alimentación de motores físicamente desconectada.'
$files = Get-ChildItem -LiteralPath $firmwarePath -Filter '*.py' |
    Where-Object { $_.Name -notlike '*.example.py' -and $_.Name -ne 'main.py' }
foreach ($file in $files) {
    & $pythonPath -m mpremote connect $Port fs cp $file.FullName (':' + $file.Name)
    if ($LASTEXITCODE -ne 0) { throw ('Falló la carga de ' + $file.Name) }
}
& $pythonPath -m mpremote connect $Port fs cp (Join-Path $firmwarePath 'main.py') ':main.py'
if ($LASTEXITCODE -ne 0) { throw 'Falló la carga de main.py' }
Write-Host 'Archivos copiados. Reiniciar y observar con mpremote connect PUERTO repl.'
