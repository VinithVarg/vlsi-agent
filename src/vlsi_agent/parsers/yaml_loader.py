"""YAML loading with strict validation."""

from __future__ import annotations

from pathlib import Path

import yaml

from vlsi_agent.models.spec import FifoSpec


def load_fifo_spec(path: Path) -> FifoSpec:
    """Load and validate a FIFO YAML spec."""
    raw_data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw_data, dict):
        raise ValueError("YAML spec must parse to a mapping")
    return FifoSpec.model_validate(raw_data)
