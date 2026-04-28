param(
    [string]$HostName = "192.168.10.20",
    [string]$UserName = "vkr",
    [string]$OutputPath = "configs\vplc_host_container_prereq_snapshot_2026-04-27.txt",
    [string]$LinuxScriptPath = "scripts\linux\inspect_vplc_runtime_for_container.sh"
)

$ErrorActionPreference = "Stop"
$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

if (-not (Test-Path -LiteralPath $LinuxScriptPath)) {
    throw "Linux inspection script not found: $LinuxScriptPath"
}

$outputDirectory = Split-Path -Parent $OutputPath
if ($outputDirectory -and -not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}

$target = "$UserName@$HostName"
Write-Host "Collecting VPLC container prerequisite snapshot from $target"
Write-Host "SSH may ask for the password of user '$UserName'."

$linuxScript = (Get-Content -LiteralPath $LinuxScriptPath -Raw) -replace "`r", ""
$tempScriptPath = Join-Path $env:TEMP "inspect_vplc_runtime_for_container.sh"
$remoteScriptPath = "/tmp/inspect_vplc_runtime_for_container.sh"
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText($tempScriptPath, $linuxScript, $utf8NoBom)

scp $tempScriptPath "${target}:$remoteScriptPath"

if ($LASTEXITCODE -ne 0) {
    throw "SCP upload failed with exit code $LASTEXITCODE"
}

ssh $target "bash $remoteScriptPath" |
    Set-Content -LiteralPath $OutputPath -Encoding UTF8

if ($LASTEXITCODE -ne 0) {
    throw "SSH snapshot command failed with exit code $LASTEXITCODE"
}

Write-Host "Snapshot saved to $OutputPath"
