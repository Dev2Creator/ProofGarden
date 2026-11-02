# Curriculum

Sixteen lessons in two tracks. The foundations track is complete; the formal
methods track is planned.

## Foundations (written)

| # | Lesson | Core idea |
| --- | --- | --- |
| 1 | [Propositional logic](01-propositional-logic/lesson.md) | connectives, truth tables, tautologies, De Morgan |
| 2 | [State machines](02-state-machines/lesson.md) | states, transitions, traces, reachability |
| 3 | [Predicates and quantifiers](03-predicate-logic/lesson.md) | ∀, ∃, and translation traps |
| 4 | [Scope and quantifier negation](04-quantifier-scope/lesson.md) | binding, capture, negation normal form |
| 5 | [Sets](05-sets/lesson.md) | operations, identities, two-inclusion proofs |
| 6 | [Relations](06-relations/lesson.md) | equivalence classes, partial orders, abstraction |
| 7 | [Functions](07-functions/lesson.md) | injective, surjective, bijective, abstraction maps |
| 8 | [Direct proof and contradiction](08-direct-and-contradiction/lesson.md) | proof templates and failure modes |
| 9 | [Induction](09-induction/lesson.md) | weak, strong, structural, loop invariants |
| 10 | [Counterexamples](10-counterexamples/lesson.md) | necessity, sufficiency, shortest witnesses |

## Formal methods (planned)

| # | Lesson | Status |
| --- | --- | --- |
| 11 | Temporal logic: LTL and CTL | planned |
| 12 | Invariants and inductive assertions | planned |
| 13 | Ghost state and history variables | planned |
| 14 | Refinement and abstraction mappings | planned |
| 15 | Concurrency: interleaving and linearisability | planned |
| 16 | Distributed systems: leader election and safety | planned |

## Review status

Lessons 3–10 were written in one pass and have **not** been independently
reviewed. Their mathematical claims, and every exercise answer, should be
checked by a second reader before the curriculum is advertised as reliable.
`docs/limitations.md` records what the tools do and do not establish; that page
is not a substitute for reviewing the prose.

## How to use a lesson

1. Read the definitions and the worked example.
2. Do the exercises on paper before running anything.
3. Check your answers with the tools:

```bash
python3 -m proofgarden logic truth-table "(P IMPLIES Q) IFF (NOT Q IMPLIES NOT P)"
python3 -m proofgarden modelcheck counter_overflow.json
python3 -m proofgarden playground --port 8000
```

4. Remember that a bounded search which stops early reports `incomplete`, not
   `verified`.

## Conventions

- `NOT`, `~` and `¬` are interchangeable in the CLI, as are `IMPLIES` and `→`.
- Models use explicit finite states; nothing here reasons about infinite state
  spaces.
- "Verified" always means exhaustive over the explored finite model.
