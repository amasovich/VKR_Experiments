param(
    [string]$HostName = "192.168.10.20",
    [string]$UserName = "vkr",
    [string]$OutputPath = "configs\vplc_host_container_smoke_snapshot_2026-04-28.txt"
)

$ErrorActionPreference = "Stop"
$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$outputDirectory = Split-Path -Parent $OutputPath
if ($outputDirectory -and -not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}

$target = "$UserName@$HostName"

$commands = @'
echo "=== VPLC container smoke snapshot ==="
date --iso-8601=seconds
hostnamectl
uname -a

echo
echo "=== Network ==="
ip -br addr
ip route

echo
echo "=== Bare-metal services ==="
systemctl is-active vplc.service || true
systemctl is-active vplc-server.service || true

echo
echo "=== Podman image and container ==="
podman image inspect localhost/vkr-vplc-runtime:2.10.0 --format '{{.Id}} {{.Created}}' || true
podman ps --filter name=vkr-vplc-runtime-smoke
podman inspect vkr-vplc-runtime-smoke --format 'id={{.Id}} image={{.ImageName}} network={{.HostConfig.NetworkMode}} status={{.State.Status}} started={{.State.StartedAt}}' || true

echo
echo "=== Ports ==="
ss -tulpn | grep -E ':1234|:50530' || true

echo
echo "=== Container logs ==="
podman logs --tail 120 vkr-vplc-runtime-smoke || true

echo
echo "=== Container data directories ==="
ls -la ~/vplc_container_data || true
ls -la ~/vplc_container_data/lib || true
ls -la ~/vplc_container_data/cache || true
ls -la ~/vplc_container_data/log || true
'@

$tempScriptPath = Join-Path $env:TEMP "collect_vplc_container_smoke_snapshot.sh"
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText($tempScriptPath, ($commands -replace "`r", ""), $utf8NoBom)

scp $tempScriptPath "${target}:/tmp/collect_vplc_container_smoke_snapshot.sh"
if ($LASTEXITCODE -ne 0) {
    throw "SCP upload failed with exit code $LASTEXITCODE"
}

ssh $target "bash /tmp/collect_vplc_container_smoke_snapshot.sh" |
    Set-Content -LiteralPath $OutputPath -Encoding UTF8

if ($LASTEXITCODE -ne 0) {
    throw "SSH snapshot command failed with exit code $LASTEXITCODE"
}

Write-Host "Snapshot saved to $OutputPath"
