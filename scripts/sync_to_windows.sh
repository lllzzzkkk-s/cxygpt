#!/usr/bin/env bash
set -euo pipefail

WIN_USER=${WIN_USER:-Administrator}
WIN_HOST=192.168.1.5

SRC_DIR="/Users/apple/Desktop/forgpt/"
DEST_DIR_WINDOWS='H:/project/cxygpt'
REMOTE_DEST='/cygdrive/h/project/cxygpt'

RSYNC_EXCLUDES=(
  '--exclude' 'node_modules/'
  '--exclude' 'venv/'
  '--exclude' '.venv/'
  '--exclude' 'apps/api-gateway/.venv/'
  '--exclude' 'apps/web/node_modules/'
  '--exclude' '__pycache__/'
  '--exclude' '.pytest_cache/'
  '--exclude' 'htmlcov/'
  '--exclude' '*.log'
)

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN_FLAG="--dry-run"
  shift
else
  DRY_RUN_FLAG=""
fi

WINDOWS_PATH_PS=${DEST_DIR_WINDOWS//\//\\}

ssh "${WIN_USER}@${WIN_HOST}" \
  "powershell -NoProfile -Command \"New-Item -ItemType Directory -Path '${WINDOWS_PATH_PS}' -Force\"" \
  >/dev/null 2>&1 || true

rsync -av ${DRY_RUN_FLAG} --delete "${RSYNC_EXCLUDES[@]}" "${SRC_DIR}" "${WIN_USER}@${WIN_HOST}:${REMOTE_DEST}" "$@"
