"""Typed IR for FIFO generation."""

from __future__ import annotations

from dataclasses import dataclass

from vlsi_agent.models.spec import FifoSpec


@dataclass(frozen=True)
class FifoPortsIR:
    """Explicit FIFO port names."""

    clk: str
    rst_n: str
    wr_en: str
    rd_en: str
    wdata: str
    rdata: str
    full: str
    empty: str


@dataclass(frozen=True)
class TestbenchIR:
    """Deterministic testbench parameters."""

    module_name: str
    write_count: int
    write_values: tuple[int, ...]


@dataclass(frozen=True)
class FifoIR:
    """FIFO generation IR."""

    family: str
    module_name: str
    data_width: int
    depth: int
    addr_width: int
    ptr_width: int
    count_width: int
    ports: FifoPortsIR
    tb: TestbenchIR


def _deterministic_values(data_width: int, write_count: int) -> tuple[int, ...]:
    """Generate a stable sequence of data values for the testbench."""
    mask = (1 << data_width) - 1
    values = []
    for index in range(write_count):
        value = ((index + 1) * 3) ^ 0x5
        values.append(value & mask)
    return tuple(values)


def build_fifo_ir(spec: FifoSpec) -> FifoIR:
    """Convert a validated FIFO spec into a typed IR."""
    depth = spec.parameters.depth
    addr_width = max(1, depth.bit_length() - 1)
    ptr_width = addr_width + 1
    count_width = ptr_width
    write_values = _deterministic_values(spec.parameters.data_width, spec.tb.write_count)
    return FifoIR(
        family=spec.design.family,
        module_name=spec.design.module_name,
        data_width=spec.parameters.data_width,
        depth=depth,
        addr_width=addr_width,
        ptr_width=ptr_width,
        count_width=count_width,
        ports=FifoPortsIR(**spec.ports.model_dump()),
        tb=TestbenchIR(
            module_name=spec.tb.module_name,
            write_count=spec.tb.write_count,
            write_values=write_values,
        ),
    )
