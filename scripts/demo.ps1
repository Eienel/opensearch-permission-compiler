param(
    [switch]$KeepCluster
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$IntegrationRoot = Join-Path $ProjectRoot "integration"
$BuildRoot = Join-Path $IntegrationRoot "build"
$Python = if ($env:PERMISSION_COMPILER_PYTHON) {
    $env:PERMISSION_COMPILER_PYTHON
} else {
    (Get-Command python).Source
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is required. Install and start Docker Desktop, then rerun."
}

function New-RandomHex {
    param([int]$ByteCount = 18)

    $bytes = New-Object byte[] $ByteCount
    $generator = [Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $generator.GetBytes($bytes)
    }
    finally {
        $generator.Dispose()
    }
    return [BitConverter]::ToString($bytes).Replace("-", "")
}

New-Item -ItemType Directory -Force -Path $BuildRoot | Out-Null

if (-not $env:OPENSEARCH_INITIAL_ADMIN_PASSWORD) {
    $env:OPENSEARCH_INITIAL_ADMIN_PASSWORD = "Q7!z-" + (New-RandomHex)
}
if (-not $env:DEMO_TEST_PASSWORD) {
    $env:DEMO_TEST_PASSWORD = "R8!y-" + (New-RandomHex)
}

$Compose = Join-Path $IntegrationRoot "compose.yaml"
$CaCert = Join-Path $BuildRoot "root-ca.pem"
$Workflow = Join-Path $IntegrationRoot "workflow.json"
$BeforeEvidence = Join-Path $BuildRoot "before-evidence.json"
$Candidate = Join-Path $BuildRoot "candidate-role.json"
$CompileReport = Join-Path $BuildRoot "compile-report.json"
$AfterEvidence = Join-Path $BuildRoot "after-evidence.json"
$Verification = Join-Path $BuildRoot "verification-report.json"
$Compiler = Join-Path $ProjectRoot "skills\permission-compiler\scripts\permission_compiler.py"
$Setup = Join-Path $IntegrationRoot "setup_cluster.py"

try {
    Write-Host "[1/7] Starting OpenSearch 3.7.0"
    docker compose -f $Compose up -d

    Write-Host "[2/7] Copying the demo CA certificate"
    $deadline = (Get-Date).AddMinutes(3)
    do {
        $previousPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        docker cp "permission-compiler-opensearch:/usr/share/opensearch/config/root-ca.pem" $CaCert 2>$null
        $copied = $LASTEXITCODE -eq 0
        $ErrorActionPreference = $previousPreference
        if ($copied -and (Test-Path -LiteralPath $CaCert)) { break }
        $containerStatus = docker inspect `
            --format '{{.State.Status}}' permission-compiler-opensearch
        if ($containerStatus -eq "exited") {
            docker logs --tail 80 permission-compiler-opensearch
            throw "OpenSearch exited before creating its demo CA certificate."
        }
        Start-Sleep -Seconds 2
    } while ((Get-Date) -lt $deadline)
    if (-not (Test-Path -LiteralPath $CaCert)) {
        throw "Could not obtain the OpenSearch demo CA certificate."
    }

    Write-Host "[3/7] Configuring a user with an empty role and seeding logs"
    & $Python $Setup setup --ca-cert $CaCert
    if ($LASTEXITCODE -ne 0) { throw "Cluster setup failed." }

    $env:OPENSEARCH_URL = "https://localhost:9200"
    $env:OPENSEARCH_USERNAME = "permission-compiler-user"
    $env:OPENSEARCH_PASSWORD = $env:DEMO_TEST_PASSWORD

    Write-Host "[4/7] Collecting safe before-role permission evidence"
    & $Python $Compiler probe --workflow $Workflow --ca-cert $CaCert `
        --skip-hostname-verification --output $BeforeEvidence
    if ($LASTEXITCODE -ne 0) { throw "Before-role probe failed." }

    Write-Host "[5/7] Compiling the observed-minimum role"
    & $Python $Compiler compile --workflow $Workflow --evidence $BeforeEvidence `
        --output $Candidate --report $CompileReport
    if ($LASTEXITCODE -ne 0) { throw "Role compilation failed review checks." }

    Write-Host "[6/7] Explicitly applying the reviewed candidate in the disposable cluster"
    & $Python $Setup apply-role --ca-cert $CaCert --candidate $Candidate
    if ($LASTEXITCODE -ne 0) { throw "Candidate application failed." }

    Write-Host "[7/7] Proving required actions pass and forbidden actions remain denied"
    & $Python $Compiler probe --workflow $Workflow --ca-cert $CaCert `
        --skip-hostname-verification --output $AfterEvidence
    if ($LASTEXITCODE -ne 0) { throw "After-role probe failed." }
    & $Python $Compiler verify --workflow $Workflow --evidence $AfterEvidence `
        --report $Verification
    if ($LASTEXITCODE -ne 0) { throw "Security contract verification failed." }

    $result = Get-Content -Raw $Verification | ConvertFrom-Json
    Write-Host ""
    Write-Host "LIVE DEMO PASSED: $($result.workflow)"
    $result.results | Format-Table step_id, expect, outcome
    Write-Host "Artifacts: $BuildRoot"
}
finally {
    Remove-Item Env:OPENSEARCH_PASSWORD -ErrorAction SilentlyContinue
    if (-not $KeepCluster) {
        Write-Host "Stopping and deleting the disposable cluster volume"
        docker compose -f $Compose down -v
    }
}
