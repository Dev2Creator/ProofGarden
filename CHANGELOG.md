# Changelog

## 0.1.0 — 2026-11-02

First usable release.

### Added
- Propositional logic engine: lexer, recursive-descent parser, AST, evaluator.
- Truth tables, tautology/contradiction classification, logical equivalence with counterexamples.
- DPLL SAT solver over Tseitin CNF (unit propagation, pure literal elimination).
- State systems with explicit transition API and JSON model loader.
- Breadth-first bounded model checker with verified / violated / incomplete outcomes.
- Invariant checking, reachability, deadlock detection, counterexample traces.
- Hoare-logic module with symbolic weakest preconditions and finite-domain VC checks.
- CLI: `logic truth-table|classify|equiv|sat`, `modelcheck`, `examples list`, `system info`.
- Browser playground: Logic Lab, State Machine Explorer, Model Checking Lab, Invariant Playground, Temporal Explorer, Curriculum Navigator (offline).
- Four example models, 60 automated tests, CI workflow, EULA, architecture and limitation docs.

### Fixed during development
- JSON model loader passed state tuples where mappings were expected.
- Loop verification conditions lost their names in reports.
- `generate`-style sampling entry point accepted 1-D input only (smoke-test bug).
- Auxiliary router loss in the (separate) MoD project was identically zero; see that repository.
