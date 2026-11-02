"""Command-line interface for ProofGarden."""

from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .. import __version__
from ..logic.parser import ParseError, parse
from ..logic.sat import solve
from ..logic.truth import check_equivalent, format_truth_table, truth_table
from ..modelchecking.explorer import Explorer
from ..state import JsonInvariant, load_system, make_state

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "examples" / "models"


def _print_json(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _formula_or_error(source: str):
    return parse(source)


# --------------------------------------------------------------------- logic


def cmd_truth_table(args: argparse.Namespace) -> int:
    expr = _formula_or_error(args.expression)
    table = truth_table(expr)
    if args.json:
        _print_json(
            {
                "formula": str(expr),
                "variables": list(table.names),
                "classification": table.classification,
                "rows": [
                    {"assignment": assignment, "result": value}
                    for assignment, value in table.rows
                ],
            }
        )
        return 0
    print(f"Formula: {expr}")
    print()
    print(format_truth_table(table))
    print()
    print(f"Classification: {table.classification}")
    if table.classification == "tautology":
        print("Every assignment satisfies the formula.")
    elif table.classification == "contradiction":
        print("No assignment satisfies the formula.")
    else:
        print("Some assignments satisfy the formula and some do not.")
    return 0


def cmd_classify(args: argparse.Namespace) -> int:
    expr = _formula_or_error(args.expression)
    table = truth_table(expr)
    if args.json:
        _print_json({"formula": str(expr), "classification": table.classification})
        return 0
    print(f"{expr} is a {table.classification}.")
    return 0


def cmd_equiv(args: argparse.Namespace) -> int:
    left = _formula_or_error(args.left)
    right = _formula_or_error(args.right)
    result = check_equivalent(left, right)
    if args.json:
        _print_json(
            {
                "left": str(left),
                "right": str(right),
                "equivalent": result.equivalent,
                "counterexample": result.counterexample,
            }
        )
        return 0 if result.equivalent else 1
    if result.equivalent:
        print("The formulas are logically equivalent.")
        return 0
    print("The formulas are NOT logically equivalent.")
    print(f"Counterexample: {result.counterexample}")
    return 1


def cmd_sat(args: argparse.Namespace) -> int:
    expr = _formula_or_error(args.expression)
    result = solve(expr)
    if args.json:
        _print_json(
            {
                "formula": str(expr),
                "satisfiable": result.satisfiable,
                "assignment": result.assignment,
            }
        )
        return 0
    if result.satisfiable:
        print("Satisfiable.")
        print(f"Model: {result.assignment}")
    else:
        print("Unsatisfiable.")
    return 0


# --------------------------------------------------------------- model check


def cmd_modelcheck(args: argparse.Namespace) -> int:
    path = Path(args.model_file)
    if not path.is_absolute() and not path.exists():
        candidate = EXAMPLES_DIR / path.name
        if candidate.exists():
            path = candidate
    if not path.exists():
        print(f"error: model file not found: {args.model_file}", file=sys.stderr)
        return 2

    system, invariants, target, expects_deadlock = load_system(path)
    explorer = Explorer(system, max_states=args.max_states, max_depth=args.max_depth)
    explored = explorer.explore()

    reports = []
    for inv in invariants:
        reports.append(explorer.check_invariant(inv.name, inv.violated_by))

    if target:
        target_state = make_state(target)
        reports.append(
            explorer.check_reachability(
                json.dumps(target, sort_keys=True),
                lambda state, ts=target_state: state == ts,
            )
        )

    if expects_deadlock is not None:
        report = explorer.check_deadlock_free()
        reports.append(report)

    payload = {
        "model": system.name,
        "file": str(path),
        "explored_states": len(explored.states),
        "explored_edges": len(explored.edges),
        "exploration_complete": explored.complete,
        "stop_reason": explored.stop_reason,
        "deadlocks": [dict(s) for s in explored.deadlocks],
        "checks": [r.to_dict() for r in reports],
    }

    if args.json:
        _print_json(payload)
        return 0

    print(f"Model: {system.name}")
    print(f"Explored {len(explored.states)} states and {len(explored.edges)} transitions.")
    if not explored.complete:
        print(f"Exploration INCOMPLETE: {explored.stop_reason}")
    print()
    for report in reports:
        marker = {"verified": "PASS", "violated": "FAIL", "incomplete": "OPEN"}[report.outcome]
        print(f"[{marker}] {report.property}")
        print(f"       {report.message}")
        if report.trace:
            print("       counterexample trace:")
            print(report.trace.format())
        print()
    return 0


def cmd_examples_list(args: argparse.Namespace) -> int:
    files: List[Path] = sorted(EXAMPLES_DIR.glob("*.json")) if EXAMPLES_DIR.exists() else []
    if args.json:
        _print_json({"examples": [f.name for f in files]})
        return 0
    if not files:
        print("No example models found.")
        return 0
    print("Example models:")
    for f in files:
        print(f"  {f.name}")
    print()
    print("Run one with: python -m proofgarden modelcheck <name>.json")
    return 0


def cmd_playground(args: argparse.Namespace) -> int:
    """Serve the offline playground on localhost."""
    import http.server
    import functools

    root = REPO_ROOT / "playground"
    if not root.is_dir():
        print(f"playground directory not found: {root}", file=sys.stderr)
        return 2
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    except OSError as exc:
        print(f"could not bind port {args.port}: {exc}", file=sys.stderr)
        return 2
    url = f"http://localhost:{args.port}"
    print(f"ProofGarden playground on {url}")
    print(f"Browser test suite on {url}/tests.html")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    finally:
        server.server_close()
    return 0


def cmd_system_info(args: argparse.Namespace) -> int:
    payload = {
        "name": "ProofGarden",
        "version": __version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "examples_dir": str(EXAMPLES_DIR),
        "note": "Educational checker: results apply to the finite model that was explored.",
    }
    if args.json:
        _print_json(payload)
        return 0
    print(f"ProofGarden {__version__}")
    print(f"Python {payload['python']} on {payload['platform']}")
    print(f"Examples: {payload['examples_dir']}")
    print(payload["note"])
    return 0


# ------------------------------------------------------------------- parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="proofgarden",
        description="Educational tools for propositional logic and bounded model checking.",
    )
    parser.add_argument("--version", action="version", version=f"proofgarden {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    logic = sub.add_parser("logic", help="propositional logic tools")
    logic_sub = logic.add_subparsers(dest="logic_command", required=True)

    tt = logic_sub.add_parser("truth-table", help="print a truth table")
    tt.add_argument("expression")
    tt.add_argument("--json", action="store_true")
    tt.set_defaults(func=cmd_truth_table)

    classify = logic_sub.add_parser("classify", help="tautology / contradiction / contingent")
    classify.add_argument("expression")
    classify.add_argument("--json", action="store_true")
    classify.set_defaults(func=cmd_classify)

    equiv = logic_sub.add_parser("equiv", help="check logical equivalence")
    equiv.add_argument("left")
    equiv.add_argument("right")
    equiv.add_argument("--json", action="store_true")
    equiv.set_defaults(func=cmd_equiv)

    sat = logic_sub.add_parser("sat", help="satisfiability via DPLL")
    sat.add_argument("expression")
    sat.add_argument("--json", action="store_true")
    sat.set_defaults(func=cmd_sat)

    mc = sub.add_parser("modelcheck", help="explore a bounded state model")
    mc.add_argument("model_file")
    mc.add_argument("--max-states", type=int, default=10_000)
    mc.add_argument("--max-depth", type=int, default=None)
    mc.add_argument("--json", action="store_true")
    mc.set_defaults(func=cmd_modelcheck)

    examples = sub.add_parser("examples", help="list bundled examples")
    examples_sub = examples.add_subparsers(dest="examples_command", required=True)
    ex_list = examples_sub.add_parser("list", help="list example model files")
    ex_list.add_argument("--json", action="store_true")
    ex_list.set_defaults(func=cmd_examples_list)

    playground = sub.add_parser("playground", help="serve the browser playground locally")
    playground.add_argument("--port", type=int, default=8000, help="port to bind (default 8000)")
    playground.set_defaults(func=cmd_playground)

    system = sub.add_parser("system", help="environment information")
    system_sub = system.add_subparsers(dest="system_command", required=True)
    info = system_sub.add_parser("info", help="print version and environment")
    info.add_argument("--json", action="store_true")
    info.set_defaults(func=cmd_system_info)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (ParseError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
