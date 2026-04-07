"""Validation tests."""

from __future__ import annotations

import pytest

from vlsi_agent.models.spec import FifoSpec


def test_fifo_spec_rejects_unknown_keys() -> None:
    """Unknown keys must be rejected."""
    with pytest.raises(Exception):
        FifoSpec.model_validate(
            {
                "design": {"family": "synchronous_fifo", "module_name": "fifo_sync"},
                "parameters": {"data_width": 8, "depth": 8},
                "ports": {
                    "clk": "clk",
                    "rst_n": "rst_n",
                    "wr_en": "wr_en",
                    "rd_en": "rd_en",
                    "wdata": "wdata",
                    "rdata": "rdata",
                    "full": "full",
                    "empty": "empty",
                },
                "tb": {"module_name": "fifo_tb", "write_count": 4},
                "unexpected": True,
            }
        )


def test_fifo_spec_rejects_non_power_of_two_depth() -> None:
    """Depth must be a power of two."""
    with pytest.raises(Exception):
        FifoSpec.model_validate(
            {
                "design": {"family": "synchronous_fifo", "module_name": "fifo_sync"},
                "parameters": {"data_width": 8, "depth": 6},
                "ports": {
                    "clk": "clk",
                    "rst_n": "rst_n",
                    "wr_en": "wr_en",
                    "rd_en": "rd_en",
                    "wdata": "wdata",
                    "rdata": "rdata",
                    "full": "full",
                    "empty": "empty",
                },
                "tb": {"module_name": "fifo_tb", "write_count": 4},
            }
        )
