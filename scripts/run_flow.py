from __future__ import annotations

import sys
from vlsi_agent.cli import main


def _normalize_argv(argv: list[str]) -> list[str]:
    """
    Support both:
      - positional spec + --output-dir
      - --spec SPEC + --outdir OUTDIR

    This keeps backward compatibility with the existing CLI while allowing
    a cleaner wrapper script.
    """
    args = list(argv[1:])

    # Convert --spec SPEC -> positional SPEC
    if "--spec" in args:
        i = args.index("--spec")
        if i + 1 >= len(args):
            raise SystemExit("error: --spec requires a value")
        spec_value = args.pop(i + 1)
        args.pop(i)
        args.insert(0, spec_value)

    # Convert --outdir OUTDIR -> --output-dir OUTDIR
    if "--outdir" in args:
        i = args.index("--outdir")
        if i + 1 >= len(args):
            raise SystemExit("error: --outdir requires a value")
        outdir_value = args.pop(i + 1)
        args.pop(i)
        args.extend(["--output-dir", outdir_value])

    return [argv[0], *args]


if __name__ == "__main__":
    sys.argv = _normalize_argv(sys.argv)
    raise SystemExit(main())
