# ProofGarden

**Learn, Explore, Verify.**

An educational laboratory for formal methods: propositional logic, state
machines, bounded model checking, and Hoare-style program reasoning — with an
offline browser playground and a curriculum.

- **Version:** 0.2.0 (see `CHANGELOG.md`)
- **Public author identity:** Aneek Mukherjee (Dev2Creator)
- **License:** Custom EULA, AS IS — see [`EULA.md`](EULA.md)
- **Status:** foundation track complete (10 of 16 lessons); formal-methods
  track in progress

---

## 1. What this is

ProofGarden is a small, working toolkit plus study material. Every claim the
tools make is produced by real computation over an explicit finite model, and
every limitation is written down.

Three dimensions:

1. **Learn** — 10 written lessons covering the four foundation units:
   propositional logic, predicate logic, sets/relations/functions, and
   mathematical reasoning.
2. **Explore** — a browser playground that runs entirely offline: truth
   tables, state-machine graphs, BFS model checking with traces.
3. **Verify** — a Python engine that computes truth tables, solves SAT by
   DPLL, explores state systems breadth-first, and checks Hoare-style
   verification conditions on a declared finite domain.

## 2. What this is not

- Not a theorem prover. No first-order reasoning, no SMT, no tactic language.
- Not a production verifier. It handles finite models and bounded exploration.
- Not a substitute for Lean, Coq, Isabelle, TLA⁺, Alloy, or Z3. It is the
  on-ramp, not the destination. `docs/limitations.md` lists every gap.

## 3. Quick start

```bash
git clone https://github.com/Dev2Creator/ProofGarden.git
cd ProofGarden
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
```

No third-party runtime dependencies. Python 3.9+.

```bash
# logic
python3 -m proofgarden logic truth-table "(P AND Q) IMPLIES P"
python3 -m proofgarden logic classify "P OR NOT P"
python3 -m proofgarden logic equiv "NOT (P AND Q)" "(NOT P) OR (NOT Q)"
python3 -m proofgarden logic sat "(P OR Q) AND NOT P"

# model checking
python3 -m proofgarden examples list
python3 -m proofgarden modelcheck counter_overflow.json

# Hoare logic
python3 -m proofgarden hoare swap

# playground on localhost
python3 -m proofgarden playground --port 8000
# then open http://localhost:8000
```

Add `--json` to any check command for machine-readable output.

## 4. Example output

```
$ python3 -m proofgarden modelcheck counter_overflow.json

Model: counter_overflow
Explored 5 states and 8 transitions.

[FAIL] invariant: counter_stays_below_4
       counterexample trace:
  0. {'count': 0}  <- (initial)
  1. {'count': 1}  <- inc
  2. {'count': 2}  <- inc
  3. {'count': 3}  <- inc
  4. {'count': 4}  <- inc
```

The trace is a proof that the negated claim holds. `violated` is a successful
result, not an error.

## 5. Features

| Area | What works today |
| --- | --- |
| Propositional logic | lexer, parser (precedence, associativity), evaluator, truth tables, classification, equivalence with counterexample |
| SAT | Tseitin CNF encoding, DPLL with unit propagation and pure-literal elimination |
| State systems | explicit states and labelled edges, JSON model format, Python API for programmatic systems |
| Model checking | BFS exploration, invariants as forbidden patterns, reachability, deadlock freedom, shortest counterexample traces, state/depth bounds |
| Hoare logic | assignment, sequencing, conditionals, annotated loops; weakest-precondition computation; verification conditions checked on a declared finite domain |
| CLI | `logic`, `modelcheck`, `hoare`, `examples`, `playground`, `system` — with `--json` |
| Playground | Logic Lab, State Machine Explorer, Model Checking Lab, Invariant Playground with repair toggle, Temporal Logic Explorer (G/F/U), curriculum tracker |

## 6. Curriculum

Ten lessons are written; six formal-methods lessons remain. Foundations are
complete.

| # | Lesson | Unit | Status |
| --- | --- | --- | --- |
| 1 | Propositional logic | Foundations | written |
| 2 | State machines | Foundations | written |
| 3 | Predicates and quantifiers | Foundations | written |
| 4 | Scope, binding, quantifier negation | Foundations | written |
| 5 | Sets and operations | Foundations | written |
| 6 | Relations and equivalence | Foundations | written |
| 7 | Functions | Foundations | written |
| 8 | Direct proof and contradiction | Foundations | written |
| 9 | Mathematical induction | Foundations | written |
| 10 | Counterexamples, necessity, sufficiency | Foundations | written |
| 11 | Temporal logic: LTL and CTL | Formal methods | planned |
| 12 | Invariants and inductive assertions | Formal methods | planned |
| 13 | Ghost state and history variables | Formal methods | planned |
| 14 | Refinement and abstraction mappings | Formal methods | planned |
| 15 | Concurrency: interleaving and linearisability | Formal methods | planned |
| 16 | Distributed systems: leader election and safety | Formal methods | planned |

Start at [`curriculum/01-propositional-logic/lesson.md`](curriculum/01-propositional-logic/lesson.md).

## 7. Testing

Three independent layers, all runnable offline:

```bash
# Python: 64 unit, integration and cross-check tests
python3 -m unittest discover -s tests -v

# JavaScript: 17 engine tests on Node's built-in runner
node --test tests/playground/*.test.js

# Browser: open the in-page assertion suite
python3 -m proofgarden playground --port 8000
# then http://localhost:8000/tests.html
```

The SAT solver is cross-checked against exhaustive truth-table enumeration on
randomly generated small formulas (`tests/test_sat_crosscheck.py`), so the two
independent implementations must agree before a build is accepted.

CI runs the Python suite on 3.9–3.12 and a compile check; see
`.github/workflows/ci.yml`.

## 8. Project structure

```
proofgarden/
  logic/            lexer, parser, AST, evaluator, truth tables, DPLL SAT
  modelchecking/    BFS explorer, invariants, reachability, deadlocks
  verification/     Hoare logic and weakest preconditions
  cli/              argparse command surface
  state.py          state systems and the JSON model format
  traces.py         structured counterexample traces
curriculum/         10 written lessons, one folder per lesson
examples/models/    four runnable models, two of them deliberately broken
playground/         self-contained HTML/CSS/JS lab, no build step
tests/              Python suites, Node suites, fixtures
docs/               architecture and limitations
scripts/            helper scripts
```

## 9. Design rules

1. **No `eval`.** Formulas are parsed into an explicit AST. User input never
   becomes Python code, and `tests/test_logic.py` asserts it.
2. **Bounded means bounded.** When the explorer hits `--max-states` or
   `--max-depth`, the outcome is `incomplete`, never `verified`.
3. **Violations carry traces.** Every negative result includes a shortest path
   from an initial state.
4. **Limits are documented.** `docs/limitations.md` is part of the product.
5. **Two engines must agree.** The Python and JavaScript logic engines are
   cross-checked on the same formulas.

## 10. Authorship and license

Public author identity: **Aneek Mukherjee (Dev2Creator)**. This is the name
used in `README.md`, `EULA.md`, `CITATION.cff`, and `pyproject.toml`. The
internal build specification (`AGENT.md`) is a private working document and is
not published with the project; where the two disagree, the public identity
above is authoritative.

Licensed under a custom end-user license — see [`EULA.md`](EULA.md). It is not
an OSI-approved open-source license. It is not legal advice and has not been
reviewed by counsel; obtain legal review before relying on it.

## 11. Roadmap

See [`ROADMAP.md`](ROADMAP.md). Next: lessons 11–16, an LTL bounded checker
over the existing explorer, a JSON schema for models, and a playground test
harness integrated into CI.
