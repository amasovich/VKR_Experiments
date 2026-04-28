#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-localhost/vkr-vplc-runtime:2.10.0}"
CONTAINER_NAME="${CONTAINER_NAME:-vkr-vplc-runtime-smoke}"
DATA_DIR="${DATA_DIR:-$HOME/vplc_container_data}"

if ss -tulpn | grep -q ':1234 '; then
    echo "Port 1234 is already in use. Stop bare-metal VPLC before running the container:"
    echo "  sudo systemctl stop vplc.service"
    echo "  sudo systemctl stop vplc-server.service"
    exit 2
fi

mkdir -p "$DATA_DIR/lib" "$DATA_DIR/cache" "$DATA_DIR/log"

podman rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true

podman run -d \
    --name "$CONTAINER_NAME" \
    --network host \
    --restart no \
    -v "$DATA_DIR/lib:/var/lib/vplc:Z,U" \
    -v "$DATA_DIR/cache:/var/cache/vplc:Z,U" \
    -v "$DATA_DIR/log:/var/log/vplc:Z,U" \
    "$IMAGE_NAME"

sleep 3

podman ps --filter "name=$CONTAINER_NAME"
ss -tulpn | grep ':1234 ' || {
    echo "Container started, but port 1234 is not listening."
    podman logs "$CONTAINER_NAME"
    exit 3
}

podman logs --tail 80 "$CONTAINER_NAME"
