#!/usr/bin/env bash
set -euo pipefail

PORT="${COMFYUI_PORT:-8188}"
WORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${WORK_DIR}/comfyui-${PORT}.pid"

if [ ! -f "${PID_FILE}" ]; then
  echo "No pid file found for port ${PORT}."
  exit 0
fi

PID="$(cat "${PID_FILE}")"
if kill -0 "${PID}" >/dev/null 2>&1; then
  kill "${PID}"
  echo "Stopped ComfyUI process ${PID}."
else
  echo "ComfyUI process ${PID} is not running."
fi

rm -f "${PID_FILE}"
