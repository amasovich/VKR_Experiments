#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-localhost/vkr-vplc-runtime:2.10.0}"
WORKDIR="${WORKDIR:-$HOME/vplc_container_profile_2026-04-27}"
DEB_SOURCE="${DEB_SOURCE:-$HOME/vplc_install_2026-04-25/vplc_latest_amd64.deb}"
CONTAINERFILE_SOURCE="${CONTAINERFILE_SOURCE:-./Containerfile}"

if [ ! -f "$CONTAINERFILE_SOURCE" ]; then
    echo "Containerfile not found: $CONTAINERFILE_SOURCE"
    exit 1
fi

mkdir -p "$WORKDIR"
cp "$DEB_SOURCE" "$WORKDIR/vplc_latest_amd64.deb"

source_abs="$(readlink -f "$CONTAINERFILE_SOURCE")"
target_abs="$(readlink -m "$WORKDIR/Containerfile")"
if [ "$source_abs" != "$target_abs" ]; then
    cp "$CONTAINERFILE_SOURCE" "$WORKDIR/Containerfile"
fi

cd "$WORKDIR"

sha256sum vplc_latest_amd64.deb
podman build -t "$IMAGE_NAME" -f Containerfile .

podman image inspect "$IMAGE_NAME" --format '{{.Id}} {{.Created}}'
