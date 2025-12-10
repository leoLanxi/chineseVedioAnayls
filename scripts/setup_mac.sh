#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
cd "$project_dir"
python3 -c "import venv,sys,os; d=os.path.join(os.getcwd(),'.venv'); venv.EnvBuilder(with_pip=True).create(d); print(d)" >/dev/null
VENV="${project_dir}/.venv"
source "${VENV}/bin/activate"
python -m pip install -r requirements.txt
if ! command -v ffmpeg >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then brew install ffmpeg; fi
fi
export MODELSCOPE_CACHE="${HOME}/.cache/modelscope"
python scripts/prefetch_models.py
echo "OK"

