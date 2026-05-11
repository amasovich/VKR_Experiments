param(
    [Parameter(Mandatory = $true)]
    [ValidateSet(
        "VPLC_L0_IDLE_10_20",
        "VPLC_L1_LIGHT_10_20",
        "VPLC_L2_MEDIUM_25_35",
        "VPLC_L3_HIGH_75_100",
        "VPLC_L3_STRESS_75_80"
    )]
    [string]$ModeId,

    [Parameter(Mandatory = $true)]
    [ValidateRange(1, 99)]
    [int]$RunNumber,

    [string]$SeriesDate = (Get-Date -Format "yyyyMMdd"),
    [string]$SeriesNumber = "S01",
    [int]$Samples = 1000,
    [int]$IntervalSec = 1,
    [string]$HostName = "192.168.10.20",
    [string]$UserName = "vkr",
    [string]$LocalRoot = "raw_logs\vplc_status",
    [string]$IdentityFile = ""
)

$ErrorActionPreference = "Stop"
$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$modeSpecs = @{
    "VPLC_L0_IDLE_10_20" = @{ LoadLevel = 0; LoadPasses = 0;   T0 = 10; Deadline = 20  }
    "VPLC_L1_LIGHT_10_20" = @{ LoadLevel = 1; LoadPasses = 32;  T0 = 10; Deadline = 20  }
    "VPLC_L2_MEDIUM_25_35" = @{ LoadLevel = 2; LoadPasses = 128; T0 = 25; Deadline = 35  }
    "VPLC_L3_HIGH_75_100" = @{ LoadLevel = 3; LoadPasses = 512; T0 = 75; Deadline = 100 }
    "VPLC_L3_STRESS_75_80" = @{ LoadLevel = 3; LoadPasses = 512; T0 = 75; Deadline = 80  }
}

$spec = $modeSpecs[$ModeId]
$target = "$UserName@$HostName"
$seriesId = "SER_${SeriesDate}_${ModeId}_${SeriesNumber}"
$runId = "RUN_${SeriesDate}_${ModeId}_${SeriesNumber}_R$($RunNumber.ToString('00'))"
$fileName = "$runId.csv"
$remoteCollector = "/tmp/collect_vplc_status_rawlogs.sh"
$remoteCsv = "/tmp/$fileName"
$localDir = Join-Path $LocalRoot $ModeId
$localCsv = Join-Path $localDir $fileName
$sshOptions = @()
if ($IdentityFile) {
    $sshOptions += @("-i", $IdentityFile)
}

if (-not (Test-Path -LiteralPath $localDir)) {
    New-Item -ItemType Directory -Path $localDir | Out-Null
}

Write-Host "Mode: $ModeId"
Write-Host "Expected load_level=$($spec.LoadLevel), load_passes=$($spec.LoadPasses), t0_ms=$($spec.T0), deadline_ms=$($spec.Deadline)"
Write-Host "RunID: $runId"
Write-Host "Samples: $Samples, interval_sec=$IntervalSec"
Write-Host ""
Write-Host "Before continuing, verify in VPLC Studio that load_level is $($spec.LoadLevel)."
Write-Host "Press Enter to start, or Ctrl+C to cancel."
Read-Host | Out-Null

scp @sshOptions ".\scripts\linux\collect_vplc_status_rawlogs.sh" "${target}:$remoteCollector"
if ($LASTEXITCODE -ne 0) {
    throw "SCP upload failed with exit code $LASTEXITCODE"
}

ssh @sshOptions $target "chmod +x $remoteCollector"
if ($LASTEXITCODE -ne 0) {
    throw "chmod failed with exit code $LASTEXITCODE"
}

$remoteCommand = "bash $remoteCollector --out $remoteCsv --mode-id $ModeId --series-id $seriesId --run-id $runId --load-level $($spec.LoadLevel) --load-passes $($spec.LoadPasses) --t0-ms $($spec.T0) --deadline-ms $($spec.Deadline) --samples $Samples --interval-sec $IntervalSec"
ssh @sshOptions $target $remoteCommand
if ($LASTEXITCODE -ne 0) {
    throw "Remote collector failed with exit code $LASTEXITCODE"
}

scp @sshOptions "${target}:$remoteCsv" $localCsv
if ($LASTEXITCODE -ne 0) {
    throw "SCP download failed with exit code $LASTEXITCODE"
}

Write-Host "Downloaded: $localCsv"
