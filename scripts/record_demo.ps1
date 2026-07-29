param(
    [string]$Ffmpeg = "ffmpeg"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$DemoRoot = Join-Path $ProjectRoot "demo"
$Transcript = Join-Path $DemoRoot "live-demo-transcript.txt"
$Video = Join-Path $DemoRoot "permission-compiler-live-demo.mp4"
$Renderer = Join-Path $PSScriptRoot "render_demo_video.py"
$Python = if ($env:PERMISSION_COMPILER_PYTHON) {
    $env:PERMISSION_COMPILER_PYTHON
} else {
    (Get-Command python).Source
}

New-Item -ItemType Directory -Force -Path $DemoRoot | Out-Null

Start-Transcript -Path $Transcript -Force | Out-Null
try {
    Write-Host "OpenSearch Permission Compiler - live disposable integration"
    Write-Host "Generated: $((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))"
    & (Join-Path $PSScriptRoot "demo.ps1")
}
finally {
    Stop-Transcript | Out-Null
}

& $Python $Renderer `
    --transcript $Transcript `
    --candidate (Join-Path $ProjectRoot "integration\build\candidate-role.json") `
    --verification (Join-Path $ProjectRoot "integration\build\verification-report.json") `
    --output $Video `
    --ffmpeg $Ffmpeg
if ($LASTEXITCODE -ne 0) {
    throw "Video rendering failed."
}

Write-Host "Rendered sanitized demo video: $Video"
