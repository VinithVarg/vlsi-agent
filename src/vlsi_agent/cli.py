"""CLI entry points for the VLSI agent flow."""

from __future__ import annotations

import argparse
from pathlib import Path

from vlsi_agent.flow import run_flow


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""
    parser = argparse.ArgumentParser(description="Run the FIFO YAML-to-RTL flow.")
    parser.add_argument("spec", type=Path, help="Path to the FIFO YAML spec.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("generated"),
        help="Directory for generated artifacts.",
    )
    parser.add_argument(
        "--skip-tools",
        action="store_true",
        help="Generate artifacts without invoking external tools.",
    )
    return parser


def main() -> int:
    """Run the CLI."""
    args = build_parser().parse_args()
    run_flow(spec_path=args.spec, output_dir=args.output_dir, run_tools=not args.skip_tools)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
