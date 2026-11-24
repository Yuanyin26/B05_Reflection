#!/bin/bash
set -euo pipefail

B05_PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "${B05_PYTHON:-}" ]]; then
    if [[ -x "$B05_PROJECT_ROOT/.venv/bin/python" ]]; then
        B05_PYTHON="$B05_PROJECT_ROOT/.venv/bin/python"
    else
        B05_PYTHON=python3
    fi
fi

exec "$B05_PYTHON" "$B05_PROJECT_ROOT/src/main.py" \
    --task all --test --check-only \
    --data-root "$B05_PROJECT_ROOT/data/examples" \
    --out-dir "$B05_PROJECT_ROOT/outputs/local" \
    "$@"
