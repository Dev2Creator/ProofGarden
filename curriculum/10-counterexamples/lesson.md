# Lesson 10 — Counterexamples, Necessity, and Sufficiency

## 1. Three different questions

For a claim `P → Q`:

- Is it **true**? If not, one counterexample settles it.
- Is `P` **necessary** for `Q`? That asks whether `¬P → ¬Q`, i.e. whether `P`
  is a condition whose absence kills `Q`.
- Is `P` **sufficient** for `Q`? That is the original claim `P → Q`.

"Necessary" and "sufficient" are not opposites. A condition can be both,
either, or neither:

| Statement | Necessary? | Sufficient? |
| --- | --- | --- |
| Divisible by 4 → even | yes | no |
| Even → divisible by 4 | no | no |
| Divisible by 8 → divisible by 4 | no | yes |
| Divisible by 4 → divisible by 2 | yes | yes |

## 2. Counterexample discipline

A counterexample must satisfy the hypothesis and violate the conclusion. Two
common errors:

1. **Irrelevant witness** — an object that fails the hypothesis (`x = 3` does
   not refute "all even numbers are divisible by 2").
2. **Near miss** — an object that satisfies the conclusion by accident, which
   refutes nothing.

In a model checker the same discipline is enforced structurally: a violation
trace is a path from an initial state to a state that breaks the property.
Every step of the trace is a legal transition, so the hypothesis is satisfied
by construction.

## 3. Smallest counterexamples

When a claim is false, the *smallest* counterexample is the most informative:
it localises the failure. The number 6 is the smallest perfect number that is
not prime; `n = 4` breaks "`n² − n + 41` is prime"; the smallest non-Desarguesian
plane has a specific finite size.

ProofGarden's breadth-first explorer returns the **shortest** violation trace
by construction, which is the model-checking version of "smallest
counterexample". Depth-first exploration would find some trace, not the
shortest one.

## 4. Refutation as a first-class result

A `violated` outcome is a successful verification result: it proves the
negation. A tool that only reports `verified` has thrown away half of the
information. This is why `CheckResult.outcome` has four values:

| Outcome | Meaning |
| --- | --- |
| `verified` | exhaustive search over the finite model found no violation |
| `violated` | a reachable violation exists, with a shortest trace |
| `incomplete` | a bound was hit; nothing is claimed |
| `not_applicable` | the property is ill-formed for this model |

`incomplete` is not a failure of the tool; it is an honest statement that the
question was not answered.

## 5. Exercise set: classify and refute

1. "If a graph is connected then every vertex has degree ≥ 2." Classify as
   necessary/sufficient, then refute or prove.
2. "A number is prime only if it is odd." True or false? Give a
   counterexample if false, and state the corrected necessity claim.
3. "Every sorted list is a list." Which of necessary/sufficient holds?
4. Take the model `counter_overflow.json`. Identify the smallest change that
   would make the invariant hold, then verify that it does.
5. Explain why a *shortest* counterexample is more useful than the first one
   found by depth-first search.

## 6. Further reading

- Pólya, *How to Solve It* (the "look for a counterexample" heuristic).
- Velleman, *How to Prove It*, §3.7.
