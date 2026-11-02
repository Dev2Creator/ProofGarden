# Lesson 7 — Functions: Injectivity, Surjectivity, Bijectivity

## 1. Definition

A function `f : A → B` assigns exactly one element of `B` to each element of
`A`. The set `A` is the **domain**, `B` the **codomain**, and
`f(A) = {f(a) : a ∈ A}` the **image** (or range).

Being a function is a property of the assignment, not of the formula: "the
mother of x" is a function; "a parent of x" is not.

## 2. The three properties

| Name | Definition | Failure example |
| --- | --- | --- |
| injective (one-to-one) | `f(a) = f(b) → a = b` | `x²` on ℤ |
| surjective (onto) | `∀b ∈ B. ∃a ∈ A. f(a) = b` | `x²` on ℤ → ℤ |
| bijective | both | — |

`f(x) = 2x` on `ℤ → ℤ` is injective but not surjective. `f(x) = x²` on `ℤ → ℤ`
is neither. `f(x) = x + 1` on `ℤ → ℤ` is both.

## 3. Why the codomain matters

`f(x) = x²` restricted to `ℝ≥0 → ℝ≥0` is bijective. The same formula on
`ℝ → ℝ` is not surjective (negative values are not hit) and not injective
(`f(2) = f(−2)`).

Injectivity and surjectivity are **relative to the stated codomain**. A claim
that omits the codomain is incomplete.

## 4. Finite sets: the counting argument

For finite `A` and `B` with `|A| = |B| = n`, the following are equivalent:
`f` is injective; `f` is surjective; `f` is bijective.

For finite sets this equivalence is a *counting* fact, not a logical one. On
infinite sets it fails: `f(x) = 2x` is injective on `ℕ` but not surjective.

## 5. Composition and inverses

- `(g ∘ f)(x) = g(f(x))`.
- If `f : A → B` is bijective, there is an inverse `f⁻¹ : B → A` with
  `f⁻¹(f(a)) = a` and `f(f⁻¹(b)) = b`.
- Bijection is exactly the condition for an inverse to exist. This is the
  reason "bijective" and "invertible" are the same word in algebra.

## 6. Connection to verification

An abstraction map `α : Concrete → Abstract` used in program analysis is a
function. Soundness requires that every concrete transition is matched by some
abstract transition after applying `α`. When `α` is not injective — the usual
case — many concrete states share one abstract state, and the analysis becomes
conservative: it may report a spurious counterexample.

This is the same quotienting idea as lesson 6, expressed with functions.

## 7. Exercises

1. Classify `f : ℤ → ℤ`, `f(x) = 3x − 1` (injective? surjective?).
2. Classify `f : ℝ → ℝ≥0`, `f(x) = x²` (state the codomain explicitly).
3. Prove: if `g ∘ f` is injective then `f` is injective.
4. Give a bijection between `ℕ` and the even naturals.
5. Explain why a non-injective abstraction map cannot be inverted, and what
   that implies for reading counterexamples from an abstract analysis.

## 8. Further reading

- Velleman, *How to Prove It*, chapter 5.
- Spivak, *Calculus*, chapter 3 (for the analytic version of injectivity).
