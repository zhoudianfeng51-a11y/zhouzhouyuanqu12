#!/usr/bin/env bash
set -euo pipefail

COMFY_DIR="/Users/a1234/Documents/comfy/ComfyUI"
PORT="${COMFYUI_PORT:-8188}"
HOST="${COMFYUI_HOST:-127.0.0.1}"
WORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_PYTHON="/Users/a1234/.local/bin/python3.12"
if [ -x "${DEFAULT_PYTHON}" ]; then
  PYTHON_BIN="${COMFYUI_PYTHON:-${DEFAULT_PYTHON}}"
  VENV_DIR="${WORK_DIR}/.venv-comfyui-py312"
else
  PYTHON_BIN="${COMFYUI_PYTHON:-python3}"
  VENV_DIR="${WORK_DIR}/.venv-comfyui"
fi
LOG_DIR="${WORK_DIR}/logs"
LOG_FILE="${LOG_DIR}/comfyui-${PORT}.log"
PID_FILE="${WORK_DIR}/comfyui-${PORT}.pid"
MODE="${1:-foreground}"

mkdir -p "${LOG_DIR}"

if [ ! -d "${COMFY_DIR}" ]; then
  echo "ComfyUI directory not found: ${COMFY_DIR}"
  exit 1
fi

if curl -fsS --max-time 2 "http://${HOST}:${PORT}/system_stats" >/dev/null 2>&1; then
  echo "ComfyUI is already running: http://${HOST}:${PORT}"
  exit 0
fi

if [ ! -d "${VENV_DIR}" ]; then
  echo "Creating local Python environment at ${VENV_DIR}"
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

if ! python -c "import torch, aiohttp, yaml, PIL" >/dev/null 2>&1; then
  echo "Installing ComfyUI dependencies. This may take a while on first run."
  python -m pip install --upgrade pip
  python -m pip install -r "${COMFY_DIR}/requirements.txt"
fi

cd "${COMFY_DIR}"

if [ "${MODE}" = "--daemon" ] || [ "${MODE}" = "daemon" ]; then
  echo "Starting ComfyUI in background at http://${HOST}:${PORT}"
  nohup "${VENV_DIR}/bin/python" main.py --listen "${HOST}" --port "${PORT}" >"${LOG_FILE}" 2>&1 &
  echo "$!" > "${PID_FILE}"

  for _ in $(seq 1 90); do
    if curl -fsS --max-time 2 "http://${HOST}:${PORT}/system_stats" >/dev/null 2>&1; then
      echo "ComfyUI is ready: http://${HOST}:${PORT}"
      echo "Log: ${LOG_FILE}"
      exit 0
    fi
    sleep 2
  done

  echo "ComfyUI did not become ready in time."
  echo "Log: ${LOG_FILE}"
  tail -80 "${LOG_FILE}" || true
  exit 1
fi

echo "Log: ${LOG_FILE}"
echo "Starting ComfyUI in foreground at http://${HOST}:${PORT}"
echo "Keep this window open while using ComfyUI."
echo "$$" > "${PID_FILE}"
exec "${VENV_DIR}/bin/python" main.py --listen "${HOST}" --port "${PORT}" 2>&1 | tee "${LOG_FILE}"
