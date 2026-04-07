# VLSI Agent FIFO Starter

This project implements a strict YAML-to-RTL flow for a v1 synchronous FIFO.

Flow:
- Parse YAML with strict Pydantic validation
- Convert the validated spec into a typed IR
- Generate deterministic SystemVerilog RTL with Jinja
- Generate deterministic SystemVerilog testbench with Jinja
- Emit wrapper scripts for Verilator, Icarus, Yosys, and OpenROAD
- Optionally execute available tools from `scripts/run_flow.py`

Quick start:

```bash
python3 -m compileall src scripts
PYTHONPATH=src python3 scripts/run_flow.py specs/fifo.yaml
```

Generated outputs are written under `generated/`.

Notes:
- Only synthesizable FIFO RTL is generated.
- The testbench is deterministic and self-checking.
- OpenROAD execution is optional because it depends on technology collateral.
# VLSI Agent: Automated RTL Generation, Lint, Simulation, and Synthesis

## Overview

This repository contains an AI-assisted VLSI design agent that accepts a hardware specification and runs an automated, reproducible design flow.

The pipeline performs:

1. specification validation
2. RTL generation
3. lint checking
4. simulation
5. synthesis
6. report/log generation

The workflow is designed so that the grader can:

**clone -> run one command -> reproduce results**

---

## Repository Contents

- `src/` - core agent implementation
- `scripts/run_flow.py` - main Python pipeline driver
- `run.sh` - single entry point required for grading
- `specs/` - sample design specifications
- `generated/` - generated outputs (logs, reports, RTL)
- `README.md` - reproduction instructions

If present, the repository may also include:

- `eda/` - EDA interaction scripts in TCL / shell / Python
- `examples/outputs/` - committed sample outputs for reference
- `tests/` - smoke/unit tests

---

## Environment and Dependencies

### Required Software

- Python 3.10 or newer
- Verilator
- Icarus Verilog (`iverilog`, `vvp`)
- Yosys

### Tested Tool Versions

The flow has been verified with:

- Verilator 5.020
- Icarus Verilog 12.0
- Icarus runtime 12.0
- Yosys 0.63+188

---

## Setup Instructions

Clone the repository:

```bash
git clone <https://github.com/VinithVarg/vlsi-agent.git>
cd vlsi-agent
