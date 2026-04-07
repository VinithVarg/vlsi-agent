"""Flow-level tests."""

from __future__ import annotations

from pathlib import Path

from vlsi_agent.flow import run_flow


def test_run_flow_generates_expected_artifacts(tmp_path: Path) -> None:
    """The flow should emit deterministic artifacts without running tools."""
    spec_path = Path("specs/fifo.yaml")
    artifacts, results, summary = run_flow(spec_path=spec_path, output_dir=tmp_path, run_tools=False)

    assert not results
    assert summary.initial_failure_stage is None
    assert summary.repair_attempts == 0
    assert summary.final_status == "not_run"
    assert artifacts.rtl_path.exists()
    assert artifacts.tb_path.exists()
    assert artifacts.verilator_path.exists()
    assert artifacts.iverilog_path.exists()
    assert artifacts.yosys_script_path.exists()
    assert artifacts.openroad_tcl_path.exists()
    assert summary.artifact_paths["rtl"] == artifacts.rtl_path
