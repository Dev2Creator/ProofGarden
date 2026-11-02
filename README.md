# ProofGarden

**Learn, Explore, Verify.**

ProofGarden is an educational laboratory for formal methods: propositional logic, state machines, invariants, bounded model checking and Hoare logic. Everything here runs locally, uses the Python standard library, and reports exactly what it checked — no overstated claims.

> **License:** distributed under a custom end-user license agreement, **not** an OSI-approved open-source license. Read [EULA.md](EULA.md) before downloading or using this project.

---

## What works today

| Area | Status |
| --- | --- |
| Propositional logic parser (no `eval`) | working |
| Truth tables, tautology/contradiction detection | working |
| Logical equivalence with counterexamples | working |
| DPLL SAT solver (Tseitin CNF + unit propagation) | working |
| State systems, BFS exploration, reachability | working |
| Invariant checking with counterexample traces | working |
| Deadlock detection | working |
| Bounded exploration with explicit "incomplete" outcome | working |
| Hoare logic: symbolic weakest preconditions + finite-domain VC checks | working, limited |
| CLI (`python -m proofgarden`) | working |
| Browser playground (logic + graphs + model checking + temporal + curriculum) | working, offline |
| Curriculum lessons | 2 of 16 written |
| Predicate logic / CTL / SMT / theorem proving | not implemented (see ROADMAP) |

---

## Install and run

Python 3.11 or newer. No third-party runtime dependencies.

```bash
git clone <this repository>
cd ProofGarden
python -m proofgarden --help
python -m proofgarden logic truth-table "(P AND Q) IMPLIES P"
python -m proofgarden modelcheck examples/models/counter_overflow.json
python -m proofgarden examples list
```

Tests use `unittest` only:

```bash
python -m unittest discover -s tests -v
```

The playground needs no server. Open `playground/index.html` in a browser; it works from `file://` because example models are embedded in `playground/js/models.js`.

---

## Real output

```
$ python -m proofgarden logic truth-table "(P AND Q) IMPLIES P"
Formula: ((P AND Q) IMPLIES P)

P     | Q     | RESULT
------+-------+-------
FALSE | FALSE | TRUE
FALSE | TRUE  | TRUE
TRUE  | FALSE | TRUE
TRUE  | TRUE  | TRUE

Classification: tautology
Every assignment satisfies the formula.
```

```
$ python -m proofgarden modelcheck counter_overflow.json
Model: counter_overflow
Explored 5 states and 8 transitions.

[FAIL] invariant: counter_stays_below_4
       Invariant 'counter_stays_below_4' is violated in a reachable state. The trace shows one path to the violation.
       counterexample trace:
  0. {'count': 0}  <- (initial)
  1. {'count': 1}  <- inc
  2. {'count': 2}  <- inc
  3. {'count': 3}  <- inc
  4. {'count': 4}  <- inc
```

Both outputs above were produced by this repository and are stable enough to serve as regression tests (`tests/test_cli.py` asserts them).

---

## Guide to the folders

```
proofgarden/          Python package
  logic/              lexer, parser, AST, evaluator, truth tables, DPLL
  modelchecking/      breadth-first bounded model checker
  verification/       Hoare logic, weakest preconditions
  cli/                argparse command-line interface
examples/models/      four executable models (success and failure)
tests/                60 automated tests
curriculum/           lessons in Markdown
docs/                 architecture and limitations
playground/           offline HTML/CSS/JS laboratory
```

---

## Semantics you can rely on

ProofGarden distinguishes three outcomes and never blurs them:

- **verified** — the entire reachable state space of the *given finite model* was explored and the property held.
- **violated** — a reachable state falsified the property; a trace is returned.
- **incomplete** — exploration stopped at a configured limit. Nothing is claimed.

A finite-state check is not a proof about arbitrary or unbounded systems. See [docs/limitations.md](docs/limitations.md).

---

## Curriculum

- `curriculum/01-propositional-logic/lesson.md` — syntax, semantics, truth tables, tautologies, De Morgan.
- `curriculum/02-state-machines/lesson.md` — transitions, reachability, invariants, counterexamples.

---

## Tests

```
$ python -m unittest discover -s tests
.....................................................
Ran 60 tests in 0.6s

OK
```

Coverage includes truth tables, operator precedence, malformed input, equivalence, SAT models, transition validity, reachability, deadlock detection, invariant preservation, counterexample traces, exploration limits and the four bundled examples.

---

## Contribution policy

Because the project uses a restrictive custom license, contributions require the owner's explicit agreement. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Citation

See [CITATION.cff](CITATION.cff).

## License summary

Source-available under the custom EULA in [EULA.md](EULA.md). Personal evaluation and learning use is permitted; redistribution, re-licensing and commercial use are not, except with written permission from the project owner. Provided **AS IS**, without warranty.
