#!/bin/bash
set -euo pipefail

B05_PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "${B05_PYTHON:-}" ]]; then
    if [[ -n "${CONDA_PREFIX:-}" && "${CONDA_PREFIX##*/}" == "b05-reflection" && -x "$CONDA_PREFIX/bin/python" ]]; then
        B05_PYTHON="$CONDA_PREFIX/bin/python"
    else
        echo "Activate Conda environment b05-reflection, or set B05_PYTHON explicitly." >&2
        exit 1
    fi
fi

exec "$B05_PYTHON" "$B05_PROJECT_ROOT/src/main.py" \
    --task all --test --check-only \
    --data-root "$B05_PROJECT_ROOT/data/examples" \
    --out-dir "$B05_PROJECT_ROOT/outputs/local" \
    "$@"
