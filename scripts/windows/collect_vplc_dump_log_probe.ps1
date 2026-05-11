param(
    [string]$HostName = "192.168.10.20",
    [string]$UserName = "vkr",
    [string]$OutputDir = "",
    [string[]]$RemoteRoots = @("/var/lib/vplc", "/var/log/vplc")
)

$ErrorActionPreference = "Stop"
$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

if (-not $OutputDir) {
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $OutputDir = "vplc\masc_vplc\dump_log_probe\probe_$stamp"
}

if (-not (Test-Path -LiteralPath $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$target = "$UserName@$HostName"
$manifestPath = Join-Path $OutputDir "probe_manifest.txt"
$remoteFileListPath = Join-Path $OutputDir "remote_files.txt"
$downloadDir = Join-Path $OutputDir "downloaded_files"

if (-not (Test-Path -LiteralPath $downloadDir)) {
    New-Item -ItemType Directory -Path $downloadDir | Out-Null
}

$remoteRootsLiteral = ($RemoteRoots | ForEach-Object { "'" + ($_ -replace "'", "'\''") + "'" }) -join " "

$commands = @"
set -u

echo "=== VPLC dump/log probe ==="
date --iso-8601=seconds
hostname

echo
echo "=== VPLC status ==="
vplc status || true

echo
echo "=== VPLC config ==="
vplc config || true

echo
echo "=== Candidate files ==="
find $remoteRootsLiteral -maxdepth 2 -type f \( -iname '*dump*' -o -iname '*log*' -o -iname '*vplc*' \) -printf '%TY-%Tm-%Td %TH:%TM:%TS %s %p\n' 2>/dev/null | sort || true

echo
echo "=== File samples ==="
while IFS= read -r file_path; do
    [ -n "`$file_path" ] || continue
    echo
    echo "--- `$file_path ---"
    stat "`$file_path" 2>/dev/null || true
    file "`$file_path" 2>/dev/null || true
    echo "[head -40]"
    head -40 "`$file_path" 2>/dev/null || true
echo "[hex first 256 bytes]"
    od -An -tx1 -N 256 "`$file_path" 2>/dev/null || true
done < <(find $remoteRootsLiteral -maxdepth 2 -type f \( -iname '*dump*' -o -iname '*log*' -o -iname '*vplc*' \) 2>/dev/null | sort)
"@

$tempScriptPath = Join-Path $env:TEMP "collect_vplc_dump_log_probe.sh"
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText($tempScriptPath, ($commands -replace "`r", ""), $utf8NoBom)

scp $tempScriptPath "${target}:/tmp/collect_vplc_dump_log_probe.sh"
if ($LASTEXITCODE -ne 0) {
    throw "SCP upload failed with exit code $LASTEXITCODE"
}

ssh $target "bash /tmp/collect_vplc_dump_log_probe.sh" |
    Set-Content -LiteralPath $manifestPath -Encoding UTF8

if ($LASTEXITCODE -ne 0) {
    throw "SSH probe command failed with exit code $LASTEXITCODE"
}

$fileListCommand = "find $remoteRootsLiteral -maxdepth 2 -type f \( -iname '*dump*' -o -iname '*log*' -o -iname '*vplc*' \) 2>/dev/null | sort"
ssh $target $fileListCommand |
    Set-Content -LiteralPath $remoteFileListPath -Encoding UTF8

if ($LASTEXITCODE -ne 0) {
    throw "SSH file list command failed with exit code $LASTEXITCODE"
}

$remoteFiles = Get-Content -LiteralPath $remoteFileListPath -Encoding UTF8 | Where-Object { $_ }
foreach ($remoteFile in $remoteFiles) {
    $safeName = ($remoteFile.TrimStart("/") -replace "[\\/:\*\?`"<>|]", "_")
    $localPath = Join-Path $downloadDir $safeName
    scp "${target}:$remoteFile" $localPath
    if ($LASTEXITCODE -ne 0) {
        Add-Content -LiteralPath $manifestPath -Encoding UTF8 -Value "DOWNLOAD_FAILED: $remoteFile"
    }
}

Write-Host "Probe saved to $OutputDir"
