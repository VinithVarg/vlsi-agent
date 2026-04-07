# VLSI Agent: Automated RTL Generation, Lint, Simulation, and Synthesis

## Overview

This repository implements an AI-assisted VLSI design agent that takes a hardware specification (YAML) and runs a fully automated design flow:

1. Specification validation
2. RTL generation
3. Lint (Verilator)
4. Simulation (Icarus Verilog)
5. Synthesis (Yosys)
6. Report and log generation

The system is designed for **one-command execution** and full reproducibility.

---

## Repository Structure

vlsi-agent/
├── README.md
├── run.sh                      # single entry point (REQUIRED)
├── requirements.txt
├── specs/                      # sample inputs
│   └── fifo.yaml
├── scripts/
│   └── run_flow.py             # main pipeline driver
├── src/                        # agent implementation
├── eda/                        # EDA scripts (if present)
├── examples/outputs/           # example outputs (logs/reports)
└── generated/                  # created during execution

---

## Setup Instructions

### 1. Clone the Repository

git clone https://github.com/VinithVarg/vlsi-agent.git
cd vlsi-agent


### 2. Create Python Environment

python3 -m venv .venv
source .venv/bin/activate

### 3. Install Dependencies

pip install -r requirements.txt


### 4. Install Required EDA Tools

Ensure the following tools are installed:

* Verilator
* Icarus Verilog (`iverilog`, `vvp`)
* Yosys

Verify installation:

verilator --version
iverilog -V
vvp -V
yosys -V

## 🚀 Single Command Execution

Run the full pipeline:

./run.sh

## Running with Custom Input

./run.sh specs/fifo.yaml


## Running with Custom Output Directory

./run.sh specs/fifo.yaml my_outputs


## Under-the-Hood Command

The system internally runs:

PYTHONPATH=src python3 scripts/run_flow.py --spec specs/fifo.yaml --outdir generated


## Input Description

The system accepts a YAML specification:

Example:

specs/fifo.yaml

The spec defines:

* module name
* parameters (width, depth, etc.)
* interface signals
* functional behavior

## Output Description

After execution, outputs are stored in:

generated/
├── logs/
├── reports/
└── rtl/

Typical outputs:

* Lint logs
* Simulation logs
* Synthesis reports
* Generated RTL


## Expected Results (Verification)

For the provided FIFO example:

### Expected Console Output

PASS: deterministic FIFO smoke test


### Expected Generated Files

generated/reports/fifo_sync.json

### Pipeline Status

All stages should pass:

* Spec validation ✔
* Verilator lint ✔
* Icarus simulation ✔
* Yosys synthesis ✔

---

## Workflow Description

The pipeline executes:

1. Parse YAML spec
2. Validate specification
3. Generate RTL
4. Run Verilator lint
5. Run Icarus simulation
6. Run Yosys synthesis
7. Save logs and reports

The process is fully automated — no manual steps required.

## Running Hidden Testcases

The system is spec-driven.

To run hidden tests:

./run.sh path/to/hidden_test.yaml


Optional output directory:

./run.sh path/to/hidden_test.yaml hidden_outputs


No code changes are required.

## Reproducibility (Grader Instructions)

The grader should be able to run:

git clone https://github.com/VinithVarg/vlsi-agent.git
cd vlsi-agent

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

./run.sh

## Verification Checklist

After running:

* ✔ `generated/rtl/` exists
* ✔ `generated/logs/` exists
* ✔ simulation shows PASS
* ✔ synthesis report generated
* ✔ `generated/reports/fifo_sync.json` exists

## Notes

* Fully automated pipeline
* No GUI required
* No manual intervention
* Designed for reproducible grading

## Author

Vinith Varghese
