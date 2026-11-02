# Lesson 1 — Propositional Logic

## 1. Intuition
A proposition is a statement that is either true or false: "it is raining", "the gate is open". Propositional logic studies how truth values combine. It is the substrate every later topic in this course builds on.

## 2. Definition
A formula is built from atoms `P, Q, R, ...` by the connectives ¬, ∧, ∨, ⊕, →, ↔ according to a grammar. A **valuation** is a map from atoms to {T, F}. A formula is:

- a **tautology** if every valuation satisfies it;
- a **contradiction** if none does;
- **contingent** otherwise.

Semantics: ¬p is true iff p is false; p ∧ q true iff both; p ∨ q true iff at least one; p ⊕ q true iff exactly one; p → q true iff ¬p or q; p ↔ q true iff equal.

## 3. Worked example
Is `(P ∧ Q) → P` a tautology? Build the table:

```
P     | Q     | P∧Q  | (P∧Q)→P
------+-------+------+--------
F     | F     | F    | T
F     | T     | F    | T
T     | F     | F    | T
T     | T     | T    | T
```

Every row is T, so yes — and you can verify it in one command:

```bash
python -m proofgarden logic truth-table "(P AND Q) IMPLIES P"
```

## 4. Common misconceptions
- **"→ is the same as ⇒."** `P → Q` is a *formula*; `P ⇒ Q` asserts the formula is valid. `P → Q` may be false.
- **"False implies anything, so implications are useless."** Vacuous truth is a feature: `if the list is empty then all its elements are prime` is genuinely true.
- **Precedence mistakes.** `¬P ∧ Q` means `(¬P) ∧ Q`, not `¬(P ∧ Q)`.

## 5. Executable exercises
```bash
python -m proofgarden logic classify "P OR NOT P"
python -m proofgarden logic classify "P AND NOT P"
python -m proofgarden logic equiv "NOT (P AND Q)" "(NOT P) OR (NOT Q)"
python -m proofgarden logic sat "(P OR Q) AND NOT P"
```
1. Predict each result before running it.
2. Find a formula that is contingent but has exactly one falsifying row.
3. Prove `P → (Q → P)` is a tautology, and explain why it looks strange.

## 6. Further reading
- S. Kleene, *Mathematical Logic* (1967) — chapters on propositional calculus.
- M. Huth & M. Ryan, *Logic in Computer Science* (2nd ed., 2004), chapter 1.
- ProofGarden source: `proofgarden/logic/` — parser and truth-table implementation.
