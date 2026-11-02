# Lesson 2 — State Machines, Reachability and Invariants

## 1. Intuition
A system is an object that is, at each moment, in exactly one of finitely many states, and moves between states when something happens. Model checking asks precise questions about all the states the system can *ever* reach.

## 2. Definition
A state-transition system is a triple (S, S₀, →) where S is a set of states, S₀ ⊆ S are the initial states, and → ⊆ S × S is the transition relation (here: labelled). The **reachable** set is the least set containing S₀ and closed under →: `Reach = S₀ ∪ { t | ∃ s ∈ Reach. s → t }`.

An **invariant** is a predicate I with `Reach ⊆ I`. A **safety property** says nothing bad ever happens — it is exactly an invariant. A **liveness** property says something good eventually happens; it needs fairness assumptions that bounded exploration does not model.

## 3. Worked example
Take the counter model:

```
0 → 1 → 2 → 3 → 4 → 0
```

With invariant `count ≤ 3` the checker finds `4` and returns a path:

```bash
python -m proofgarden modelcheck counter_overflow.json
```

Expected output includes the trace `0, 1, 2, 3, 4`, which is why the repository ships this file as a regression test.

## 4. Common misconceptions
- **"No counterexample found means the invariant holds."** Only if exploration was complete. ProofGarden prints `incomplete` otherwise — read that word carefully.
- **"Deadlock means a crash."** Deadlock means "no outgoing transition". Sometimes that is intended (a terminal state); the model must say so.
- **"Model checking proves the program correct."** It proves that the *model* has the property. If the model is wrong, so is the proof.

## 5. Exercises
1. Add a `pause` transition to `traffic_light.json` and re-run the deadlock check. Predict the outcome first.
2. Remove the `reset` edge from `counter_overflow.json`. Does the invariant still fail? Does a deadlock appear?
3. Write a model where an invariant holds but a deadlock exists, and one where both fail.

## 6. Further reading
- C. Baier & J.-P. Katoen, *Principles of Model Checking* (2008), chapters 2–3.
- E. M. Clarke et al., *Model Checking* (2000).
- ProofGarden source: `proofgarden/modelchecking/explorer.py`, `docs/limitations.md`.
