# AGENTS.md

This project is a VLSI YAML-to-RTL generator.
Current supported design family:
- synchronous FIFO only

Rules:
- Only generate synthesizable SystemVerilog.
- Use strict Pydantic validation before generation.
- Convert YAML to typed IR before RTL generation.
- Do not change YAML schemas unless explicitly asked.
- Prefer minimal code changes.
- Prefer deterministic Jinja template generation over free-form HDL generation.
- Keep deterministic Jinja generation as the base flow.
- Keep imports relative to PYTHONPATH=src.
- Do not invent ports or parameters not present in the validated spec.
- For v1, only support a synchronous FIFO design family.
- When changing files, keep functions small and typed.
- Repair loop may only modify generated RTL or the RTL-generation template unless explicitly required.
- Max repair attempts: 2
- After edits and any repair-related change, run:
  1. python3 -m compileall src scripts
  2. PYTHONPATH=src python3 scripts/run_flow.py --skip-tools specs/fifo.yaml
  3. PYTHONPATH=src python3 scripts/run_flow.py specs/fifo.yaml
- Separate repo-code failures from external environment failures.
- Do not claim success unless lint, sim, and synth pass.

