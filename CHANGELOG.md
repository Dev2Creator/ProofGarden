# Changelog

## Unreleased

### Corrected
- Public author name corrected to Anika Mukherjee (Dev2Creator) and the project
  contact address filled in as cuteypieanika@gmail.com across README, EULA, CITATION.cff,
  CODE_OF_CONDUCT, SECURITY and pyproject.toml.

## 0.2.0 — 2026-11-02

Curriculum and verification hardening.

### Added
- Eight new lessons completing the foundations track (quantifiers, scope and
  negation, sets, relations, functions, direct proof, induction, counterexamples).
- `python3 -m proofgarden playground --port N` serves the playground on localhost.
- `playground/tests.html` browser-side assertion suite, plus Node-runner mirrors
  in `tests/playground/`.
- `tests/test_sat_crosscheck.py`: DPLL results compared against exhaustive
  enumeration on 400 randomly generated formulas, including model validation.
- EULA sections on contribution ownership and on the need for independent legal
  review.

### Changed
- README rewritten: real clone URL, curriculum status table, three-layer test
  instructions, explicit authorship and verification sections.
- Public author identity standardised as Anika Mukherjee (Dev2Creator) across
  README, EULA, CITATION.cff and pyproject.toml.

### Review status
- Lessons 3–10 have not been independently reviewed. Treat their prose and
  exercise answers as drafts pending review.

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
