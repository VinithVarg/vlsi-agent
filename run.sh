#!/usr/bin/env bash
set -euo pipefail

SPEC="${1:-specs/fifo.yaml}"
OUTDIR="${2:-generated}"

echo "[INFO] Running VLSI agent flow"
echo "[INFO] Spec:   ${SPEC}"
echo "[INFO] Outdir: ${OUTDIR}"

mkdir -p "${OUTDIR}"

PYTHONPATH=src python3 scripts/run_flow.py --spec "${SPEC}" --outdir "${OUTDIR}"

echo "[INFO] Flow completed successfully"
echo "[INFO] Outputs written to ${OUTDIR}"
