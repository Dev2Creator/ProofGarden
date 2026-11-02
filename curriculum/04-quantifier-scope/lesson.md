# Lesson 4 — Scope, Binding, and Quantifier Negation

## 1. Free and bound variables

In `∀x. P(x, y)` the occurrence of `x` is **bound** by the quantifier; the
occurrence of `y` is **free**. A formula with no free variables is a
**sentence**; only sentences have a definite truth value.

## 2. Scope

A quantifier's scope is the subformula it governs.

- `∀x. (P(x) → Q(x))` — the quantifier reaches both `P` and `Q`.
- `(∀x. P(x)) → Q(x)` — the final `x` is **free**: it is not the same variable
  as the bound one. This formula is a sentence only if `Q`'s argument is
  bound elsewhere.

Scope mistakes are the most common source of "obviously true" formulas that
turn out false. When in doubt, add parentheses.

## 3. Capture and substitution

Substituting `y` for `x` in `∃y. R(x, y)` naively gives `∃y. R(y, y)`, which
changes meaning: `y` was captured by the quantifier. The correct result
renames the bound variable first: `∃z. R(y, z)`.

Rule: **substitution must not capture free variables.**

## 4. Quantifier negation laws

The four laws below hold in classical logic with a non-empty domain:

1. `¬∀x. P(x)  ≡  ∃x. ¬P(x)`
2. `¬∃x. P(x)  ≡  ∀x. ¬P(x)`
3. `∀x. P(x)   ≡  ¬∃x. ¬P(x)`
4. `∃x. P(x)   ≡  ¬∀x. ¬P(x)`

They are the predicate-level analogue of De Morgan's laws, and they are how
proofs by contradiction about "all" behave.

## 5. Worked example: negating a mixed formula

Negate: "every student passes some exam."

Step 1, formalise: `∀s. (Student(s) → ∃e. (Exam(e) ∧ Passes(s, e)))`.

Step 2, negate and push inwards:

```
¬∀s. (Student(s) → ∃e. (Exam(e) ∧ Passes(s, e)))
≡ ∃s. ¬(Student(s) → ∃e. ...)                  (law 1)
≡ ∃s. (Student(s) ∧ ¬∃e. (Exam(e) ∧ Passes(s, e)))   (implication law)
≡ ∃s. (Student(s) ∧ ∀e. ¬(Exam(e) ∧ Passes(s, e)))   (law 2)
≡ ∃s. (Student(s) ∧ ∀e. (Exam(e) → ¬Passes(s, e)))
```

Reading back: "some student fails every exam." This matches the exercise in
lesson 3.

## 6. Exercises

1. Negate `∃x. ∀y. R(x, y)` step by step.
2. Is `∀x. ∃y. R(x, y) → ∃y. ∀x. R(x, y)` valid? If not, give a two-element
   countermodel.
3. Rewrite `∀x. (P(x) → ¬Q(x))` in negation-normal form (only ¬ on atoms).
4. Explain why substitution into `∃x. R(x, y)` requires renaming.

## 7. Further reading

- Enderton, §2.4 (substitution and alphabetic variants).
- Huth & Ryan, *Logic in Computer Science*, §2.1.
