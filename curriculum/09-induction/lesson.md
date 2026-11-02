# Lesson 9 — Mathematical Induction

## 1. The principle

To prove `∀n ∈ ℕ. P(n)`:

1. **Base case:** prove `P(0)`.
2. **Inductive step:** prove `P(n) → P(n+1)` for an arbitrary `n`.
3. Conclude `∀n. P(n)`.

The inductive hypothesis is `P(n)` for *that fixed arbitrary n*, not for all
`n`. Confusing the two is the standard mistake.

## 2. A worked example

Claim: `1 + 2 + … + n = n(n+1)/2`.

```
Base: n = 0. LHS = 0, RHS = 0. ✓
Step: assume the claim for n. Then
  1 + … + n + (n+1) = n(n+1)/2 + (n+1)
                    = (n+1)(n/2 + 1)
                    = (n+1)(n+2)/2,
  which is the claim for n+1.  ∎
```

## 3. Strong induction

Assume `P(k)` for **all** `k < n`, prove `P(n)`. Equivalent in power to the
basic principle, but more convenient for recursive structures: every integer
`n ≥ 2` factors into primes, because either it is prime, or it is `ab` with
`a, b < n` and both factor by strong induction.

## 4. Structural induction

The same idea applies to recursively defined objects. For a list `xs`:

- base: `P([])`;
- step: `P(xs) → P(x : xs)`.

For trees: prove for leaves and for each node given the property for children.

This is the induction principle actually used in program verification: a
recursive function's specification is proved by structural induction on the
input, and a loop's invariant is the fixpoint of a similar argument.

## 5. Induction and loop invariants

A `while` loop with invariant `I` uses three obligations:

| Obligation | Role |
| --- | --- |
| `pre → I` | initialisation |
| `I ∧ guard → wp(body, I)` | preservation |
| `I ∧ ¬guard → post` | exit |

That is induction with the loop guard playing the role of "still going". One
further obligation — `I ∧ guard` must decrease a well-founded measure — gives
termination. ProofGarden checks the first three on a finite domain; it does
not check termination, which requires a ranking function argument.

Run the Hoare example to see the obligations printed:

```
python -m proofgarden hoare swap
```

## 6. Common failure modes

1. Proving the step only for the base case (no arbitrary `n`).
2. Assuming `P(n+1)` — circularity.
3. Missing a second base case, as in Fibonacci-style recurrences.
4. Proving a stronger statement is sometimes *easier*: strengthening the
   induction hypothesis is a legitimate and common technique.

## 7. Exercises

1. Prove `Σᵢ₌₀ⁿ 2ⁱ = 2ⁿ⁺¹ − 1`.
2. Prove every `n ≥ 4` is a sum of 2s and 5s.
3. Prove by structural induction: reversing a list twice returns the original.
4. Prove that your favourite loop's invariant is preserved by its body, and
   state the ranking function that shows termination.

## 8. Further reading

- Velleman, *How to Prove It*, chapter 6.
- Rosen, *Discrete Mathematics*, chapter 5.
