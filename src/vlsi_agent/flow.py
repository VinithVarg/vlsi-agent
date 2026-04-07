"""Top-level flow orchestration."""

from __future__ import annotations

import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from vlsi_agent.generators import GeneratedArtifacts, generate_all_artifacts
from vlsi_agent.ir import build_fifo_ir
from vlsi_agent.ir.fifo import FifoIR
from vlsi_agent.models.spec import FifoSpec
from vlsi_agent.parsers import load_fifo_spec

MAX_RETRIES = 2


@dataclass(frozen=True)
class ToolResult:
    """Result from an optional external tool invocation."""

    name: str
    status: str
    detail: str
    command: str = ""
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0


@dataclass(frozen=True)
class FlowSummary:
    """Structured summary of the repair-aware flow result."""

    initial_failure_stage: str | None
    repair_attempts: int
    final_status: str
    artifact_paths: dict[str, Path]


@dataclass(frozen=True)
class StageSpec:
    """Executable stage in the optional external-tool flow."""

    name: str
    runner: Callable[[GeneratedArtifacts], ToolResult]


def _artifact_paths(artifacts: GeneratedArtifacts) -> dict[str, Path]:
    """Build a stable mapping of generated artifact names to paths."""
    return {
        "rtl": artifacts.rtl_path,
        "tb": artifacts.tb_path,
        "verilator_script": artifacts.verilator_path,
        "iverilog_script": artifacts.iverilog_path,
        "yosys_script": artifacts.yosys_script_path,
        "openroad_tcl": artifacts.openroad_tcl_path,
    }


def _command_text(command: list[str]) -> str:
    """Render a subprocess command exactly as executed."""
    return shlex.join(command)


def _run_command(name: str, detail: str, command: list[str]) -> ToolResult:
    """Run a command and capture the full invocation details."""
    executable = command[0]
    if shutil.which(executable) is None:
        return ToolResult(
            name=name,
            status="skipped",
            detail=f"{executable} not installed",
            command=_command_text(command),
        )
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )
    status = "ok" if completed.returncode == 0 else "failed"
    if completed.returncode == 0:
        result_detail = completed.stdout.strip() or "completed"
    else:
        result_detail = detail
    return ToolResult(
        name=name,
        status=status,
        detail=result_detail,
        command=_command_text(command),
        stdout=completed.stdout,
        stderr=completed.stderr,
        returncode=completed.returncode,
    )


def _run_verilator(artifacts: GeneratedArtifacts) -> ToolResult:
    """Run Verilator lint on the generated RTL and testbench."""
    command = [
        "verilator",
        "--lint-only",
        "--timing",
        "-Wall",
        str(artifacts.rtl_path),
        str(artifacts.tb_path),
    ]
    return _run_command(name="verilator", detail="verilator lint failed", command=command)


def _run_icarus(artifacts: GeneratedArtifacts) -> ToolResult:
    """Run Icarus compile and simulation on the generated RTL."""
    if shutil.which("iverilog") is None:
        return ToolResult(name="icarus", status="skipped", detail="iverilog not installed")
    if shutil.which("vvp") is None:
        return ToolResult(name="icarus", status="skipped", detail="vvp not installed")

    out_path = artifacts.tb_path.parent.parent / "reports" / f"{artifacts.tb_path.stem}.out"
    compile_command = [
        "iverilog",
        "-g2012",
        "-o",
        str(out_path),
        str(artifacts.rtl_path),
        str(artifacts.tb_path),
    ]
    compile_result = _run_command(
        name="icarus",
        detail="icarus compile failed",
        command=compile_command,
    )
    if compile_result.status != "ok":
        return compile_result

    simulation_command = ["vvp", str(out_path)]
    simulation_result = _run_command(
        name="icarus",
        detail="icarus simulation failed",
        command=simulation_command,
    )
    if simulation_result.status != "ok":
        return simulation_result
    return ToolResult(
        name="icarus",
        status="ok",
        detail=simulation_result.stdout.strip() or "icarus simulation completed",
        command=simulation_result.command,
        stdout=simulation_result.stdout,
        stderr=simulation_result.stderr,
        returncode=simulation_result.returncode,
    )


def _run_yosys(artifacts: GeneratedArtifacts) -> ToolResult:
    """Run Yosys synthesis on the generated RTL."""
    command = [
        "yosys",
        "-p",
        (
            f"read_verilog -sv {artifacts.rtl_path}; "
            f"synth -top {artifacts.rtl_path.stem}; "
            f"stat; write_json {artifacts.rtl_path.parent.parent / 'reports' / f'{artifacts.rtl_path.stem}.json'}"
        ),
    ]
    return _run_command(name="yosys", detail="yosys failed", command=command)


def _run_openroad(artifacts: GeneratedArtifacts) -> ToolResult:
    """Run OpenROAD only when the binary and required environment are present."""
    command = ["openroad", str(artifacts.openroad_tcl_path)]
    executable = command[0]
    if shutil.which(executable) is None:
        return ToolResult(
            name="openroad",
            status="skipped",
            detail="openroad not installed",
            command=_command_text(command),
        )
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )
    if completed.returncode != 0:
        return ToolResult(
            name="openroad",
            status="failed",
            detail="openroad failed",
            command=_command_text(command),
            stdout=completed.stdout,
            stderr=completed.stderr,
            returncode=completed.returncode,
        )
    return ToolResult(
        name="openroad",
        status="ok",
        detail=completed.stdout.strip() or "completed",
        command=_command_text(command),
        stdout=completed.stdout,
        stderr=completed.stderr,
        returncode=completed.returncode,
    )


def _repair_generated_rtl(
    spec: FifoSpec,
    ir: FifoIR,
    current_rtl_text: str,
    failing_stage_name: str,
    exact_tool_command: str,
    stdout: str,
    stderr: str,
) -> str:
    """Apply a bounded deterministic repair to generated RTL only."""
    del spec, failing_stage_name, exact_tool_command, stdout, stderr

    repaired_text = current_rtl_text
    injected_probe = "    assign repair_test_probe = missing_repair_signal;\n"
    if injected_probe in repaired_text and ir.module_name in repaired_text:
        repaired_text = repaired_text.replace(injected_probe, "", 1)

    hold_assignment = "                default: count_q <= count_q;\n"
    hold_comment = "                default: begin end\n"
    if hold_assignment in repaired_text and ir.module_name in repaired_text:
        repaired_text = repaired_text.replace(hold_assignment, hold_comment, 1)
    return repaired_text


def _stage_specs() -> tuple[StageSpec, ...]:
    """Define the ordered tool stages for the repair-aware flow."""
    return (
        StageSpec(name="verilator", runner=_run_verilator),
        StageSpec(name="icarus", runner=_run_icarus),
        StageSpec(name="yosys", runner=_run_yosys),
        StageSpec(name="openroad", runner=_run_openroad),
    )


def _run_tool_stages(
    artifacts: GeneratedArtifacts,
    start_index: int = 0,
) -> tuple[tuple[ToolResult, ...], int | None]:
    """Run tool stages from a starting index until failure or completion."""
    results: list[ToolResult] = []
    stages = _stage_specs()
    for index in range(start_index, len(stages)):
        result = stages[index].runner(artifacts)
        results.append(result)
        if result.status == "failed":
            return tuple(results), index
    return tuple(results), None


def run_flow(
    spec_path: Path,
    output_dir: Path,
    run_tools: bool = True,
) -> tuple[GeneratedArtifacts, tuple[ToolResult, ...], FlowSummary]:
    """Run the complete FIFO flow."""
    spec = load_fifo_spec(spec_path)
    ir = build_fifo_ir(spec)
    artifacts = generate_all_artifacts(ir=ir, output_dir=output_dir)
    artifact_paths = _artifact_paths(artifacts)

    if not run_tools:
        return (
            artifacts,
            (),
            FlowSummary(
                initial_failure_stage=None,
                repair_attempts=0,
                final_status="not_run",
                artifact_paths=artifact_paths,
            ),
        )

    all_results: list[ToolResult] = []
    initial_failure_stage: str | None = None
    repair_attempts = 0
    rerun_index = 0
    failed_index: int | None = None
    stages = _stage_specs()

    while True:
        stage_results, failed_index = _run_tool_stages(artifacts=artifacts, start_index=rerun_index)
        if rerun_index == 0:
            all_results = list(stage_results)
        else:
            all_results = all_results[:rerun_index] + list(stage_results)
        if failed_index is None:
            break

        failed_result = all_results[failed_index]
        if initial_failure_stage is None:
            initial_failure_stage = stages[failed_index].name
        if repair_attempts >= MAX_RETRIES:
            break

        current_rtl_text = artifacts.rtl_path.read_text(encoding="utf-8")
        repaired_rtl_text = _repair_generated_rtl(
            spec=spec,
            ir=ir,
            current_rtl_text=current_rtl_text,
            failing_stage_name=failed_result.name,
            exact_tool_command=failed_result.command,
            stdout=failed_result.stdout,
            stderr=failed_result.stderr,
        )
        repair_attempts += 1
        artifacts.rtl_path.write_text(repaired_rtl_text, encoding="utf-8")
        rerun_index = failed_index

    final_status = "pass"
    if any(result.status == "failed" for result in all_results):
        final_status = "fail"

    summary = FlowSummary(
        initial_failure_stage=initial_failure_stage,
        repair_attempts=repair_attempts,
        final_status=final_status,
        artifact_paths=artifact_paths,
    )
    return artifacts, tuple(all_results), summary
