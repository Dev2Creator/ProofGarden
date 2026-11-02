# Architecture

```
playground/  ──(duplicated logic, same semantics)──  proofgarden/logic
     │                                                     │
     └── modelchecker.js  ──(same outcomes)──  proofgarden/modelchecking
```

## Python package

- `logic/lexer.py` — character-level tokens; rejects anything outside the grammar.
- `logic/parser.py` — recursive descent; precedence IFF < IMPLIES < OR < XOR < AND < NOT.
- `logic/ast.py` — frozen dataclasses; formulas are hashable values.
- `logic/truth.py` — evaluation, truth tables, equivalence with counterexample.
- `logic/sat.py` — Tseitin CNF encoder plus a DPLL solver with unit propagation and pure literal elimination.
- `state.py` — `State` is a sorted tuple of `(name, value)` pairs; `StateSystem` exposes `successors()`; JSON loader builds explicit-edge systems.
- `modelchecking/explorer.py` — BFS with parent pointers; three honest outcomes; invariant, reachability and deadlock checks.
- `verification/hoare.py` — expression and command ASTs, substitution, symbolic WP, finite-domain VC checking, concrete interpreter.
- `cli/main.py` — argparse interface with `--json` everywhere it matters.

## Design rules

1. No `eval`/`exec` on user input anywhere.
2. Every result states the scope it was computed over.
3. Bugs that were found during development became regression tests.
4. The browser engine mirrors the Python engine; a cross-check script compares classifications on shared formulas.

## Playground

Vanilla ES modules in plain script tags: `logic.js` (parser/truth tables), `modelchecker.js` (BFS/temporal operators), `models.js` (embedded examples), `app.js` (UI wiring, SVG graph, localStorage progress). No build step, no frameworks, no network.
