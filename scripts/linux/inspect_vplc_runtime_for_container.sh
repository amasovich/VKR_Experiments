#!/usr/bin/env bash
set -u

echo "=== VPLC container prerequisite inspection ==="
date --iso-8601=seconds
hostnamectl
uname -a

echo
echo "=== Network ==="
ip -br addr
ip route

echo
echo "=== Podman ==="
command -v podman || true
podman --version 2>/dev/null || true
podman info --format '{{.Host.OCIRuntime.Name}} {{.Host.Arch}} {{.Store.GraphRoot}} {{.Host.Security.Rootless}}' 2>/dev/null || true

echo
echo "=== VPLC packages ==="
dpkg -l | grep -E '^(ii)\s+(vplc|vplc-server)\s' || true
command -v vplc || true
command -v vplc-server || true

echo
echo "=== VPLC service units ==="
systemctl status vplc --no-pager || true
systemctl cat vplc --no-pager || true

echo
echo "=== VPLC Server service units ==="
systemctl status vplc-server --no-pager || true
systemctl cat vplc-server --no-pager || true

echo
echo "=== VPLC package file list ==="
dpkg -L vplc 2>/dev/null | sort || true

echo
echo "=== VPLC Server package file list ==="
dpkg -L vplc-server 2>/dev/null | sort || true

echo
echo "=== VPLC process and ports ==="
ps -ef | grep -E 'vplc|VPLC' | grep -v grep || true
ss -tulpn | grep -E '1234|50530|vplc' || true

echo
echo "=== VPLC CLI state ==="
vplc config || true
vplc status || true

echo
echo "=== VPLC Server CLI state ==="
vplc-server config || true
vplc-server status || true

echo
echo "=== Installed package files under common writable locations ==="
find /home/vkr -maxdepth 5 \( -iname '*vplc*' -o -iname '*.dump' -o -iname '*.log' \) 2>/dev/null | sort || true
sudo -n find /etc /opt /usr/local /var -maxdepth 5 \( -iname '*vplc*' -o -iname '*.dump' -o -iname '*.log' \) 2>/dev/null | sort || echo "sudo find skipped: passwordless sudo is not available in this SSH run"

echo
echo "=== Local installer cache ==="
ls -la /home/vkr/vplc_install_2026-04-25 2>/dev/null || true
sha256sum /home/vkr/vplc_install_2026-04-25/*.deb 2>/dev/null || true
