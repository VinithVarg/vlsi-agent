"""Deterministic artifact generation for FIFO flows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from vlsi_agent.ir.fifo import FifoIR


@dataclass(frozen=True)
class GeneratedArtifacts:
    """Paths to generated artifacts."""

    rtl_path: Path
    tb_path: Path
    verilator_path: Path
    iverilog_path: Path
    yosys_script_path: Path
    openroad_tcl_path: Path


def _build_environment() -> Environment:
    """Create a strict Jinja environment."""
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    return Environment(
        loader=FileSystemLoader(template_dir),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def _hex_literal(value: int, width: int) -> str:
    """Format a SystemVerilog hex literal deterministically."""
    digits = max(1, (width + 3) // 4)
    return f"{width}'h{value:0{digits}X}"


def generate_all_artifacts(ir: FifoIR, output_dir: Path) -> GeneratedArtifacts:
    """Generate RTL, TB, and tool wrapper scripts."""
    env = _build_environment()

    rtl_dir = output_dir / "rtl"
    tb_dir = output_dir / "tb"
    scripts_dir = output_dir / "scripts"
    reports_dir = output_dir / "reports"
    for directory in (rtl_dir, tb_dir, scripts_dir, reports_dir):
        directory.mkdir(parents=True, exist_ok=True)

    rtl_path = rtl_dir / f"{ir.module_name}.sv"
    tb_path = tb_dir / f"{ir.tb.module_name}.sv"
    verilator_path = scripts_dir / "run_verilator.sh"
    iverilog_path = scripts_dir / "run_iverilog.sh"
    yosys_script_path = scripts_dir / "run_yosys.sh"
    openroad_tcl_path = scripts_dir / "openroad_flow.tcl"

    tb_values = [_hex_literal(value, ir.data_width) for value in ir.tb.write_values]
    context = {
        "ir": ir,
        "output_dir": output_dir.as_posix(),
        "tb_values": tb_values,
    }

    rtl_path.write_text(env.get_template("fifo.sv.j2").render(context), encoding="utf-8")
    tb_path.write_text(env.get_template("fifo_tb.sv.j2").render(context), encoding="utf-8")
    verilator_path.write_text(
        env.get_template("run_verilator.sh.j2").render(context),
        encoding="utf-8",
    )
    iverilog_path.write_text(
        env.get_template("run_iverilog.sh.j2").render(context),
        encoding="utf-8",
    )
    yosys_script_path.write_text(
        env.get_template("run_yosys.sh.j2").render(context),
        encoding="utf-8",
    )
    openroad_tcl_path.write_text(
        env.get_template("openroad_flow.tcl.j2").render(context),
        encoding="utf-8",
    )

    for path in (verilator_path, iverilog_path, yosys_script_path):
        path.chmod(0o755)

    return GeneratedArtifacts(
        rtl_path=rtl_path,
        tb_path=tb_path,
        verilator_path=verilator_path,
        iverilog_path=iverilog_path,
        yosys_script_path=yosys_script_path,
        openroad_tcl_path=openroad_tcl_path,
    )
