param(
    [string]$HostName = "192.168.10.20",
    [string]$UserName = "vkr",
    [string]$RemoteDir = "/home/vkr/vplc_container_profile_2026-04-27"
)

$ErrorActionPreference = "Stop"

$target = "$UserName@$HostName"

$files = @(
    @{ Path = "vplc\masc_vplc\container_profile\Containerfile"; Name = "Containerfile" },
    @{ Path = "scripts\linux\build_vplc_container_image.sh"; Name = "build_vplc_container_image.sh" },
    @{ Path = "scripts\linux\run_vplc_container_smoke.sh"; Name = "run_vplc_container_smoke.sh" }
)

foreach ($file in $files) {
    if (-not (Test-Path -LiteralPath $file.Path)) {
        throw "Required file not found: $($file.Path)"
    }
}

Write-Host "Creating remote directory $RemoteDir on $target"
ssh $target "mkdir -p '$RemoteDir'"
if ($LASTEXITCODE -ne 0) {
    throw "Remote mkdir failed with exit code $LASTEXITCODE"
}

foreach ($file in $files) {
    Write-Host "Uploading $($file.Path)"
    $content = (Get-Content -LiteralPath $file.Path -Raw) -replace "`r", ""
    $tempPath = Join-Path $env:TEMP $file.Name
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($tempPath, $content, $utf8NoBom)
    scp $tempPath "${target}:$RemoteDir/$($file.Name)"
    if ($LASTEXITCODE -ne 0) {
        throw "SCP upload failed for $($file.Path) with exit code $LASTEXITCODE"
    }
}

ssh $target "chmod +x '$RemoteDir/build_vplc_container_image.sh' '$RemoteDir/run_vplc_container_smoke.sh'"
if ($LASTEXITCODE -ne 0) {
    throw "Remote chmod failed with exit code $LASTEXITCODE"
}

Write-Host "Container profile deployed to $RemoteDir"
