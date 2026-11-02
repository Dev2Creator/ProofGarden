# Limitations

ProofGarden is deliberately small. This page states exactly what it does not do.

## Model checking
- Exploration is **bounded**: `--max-states` (default 10,000) and `--max-depth` (optional).
- If a bound is hit the outcome is `incomplete`, never `verified`.
- Models are explicit state/edge tables in JSON. There is no symbolic representation, no BDDs, no partial-order reduction.
- No fairness assumptions, so "liveness" results are reachability results in disguise.
- No CTL or full LTL model checking. The playground evaluates G/F/U over the explored finite graph only.
- Infinite-state systems cannot be represented. Nothing here proves properties of unbounded systems.

## Invariants
- JSON invariants are *forbidden state patterns*: a state violates an invariant when every key/value pair in the pattern matches.
- This subset semantics cannot express relational invariants (for example `sum of accounts is constant`) in JSON. Use the Python API for those.

## Hoare logic
- Supported: assignment, sequence, if/else, while with a required invariant.
- Weakest preconditions for loops follow the standard rule; the invariant is supplied, not inferred.
- Verification conditions are checked over a **finite integer domain** (default 0..10). That is evidence, not a proof.
- No arrays, pointers, procedures, recursion, or aliasing.

## Propositional logic
- Max 16 variables for exhaustive truth tables in the CLI (12 in the browser).
- The DPLL solver is educational: no clause learning, no watched literals, no parallelisation.
- Syntax is propositional only; there are no quantifiers (see ROADMAP).

## Browser playground
- Works offline from `file://`; example models are embedded in JavaScript.
- No account system, no telemetry, no network requests.
- Learning progress lives in `localStorage` and can be cleared by the user at any time.

## Not implemented (and not claimed)
Predicate logic, sets/relations tooling, SMT solving, abstract interpretation, type theory, theorem proving, distributed-systems checkers, and an external-tool guide. See ROADMAP.md.
