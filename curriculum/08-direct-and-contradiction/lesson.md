# Lesson 8 — Direct Proof and Proof by Contradiction

## 1. The shape of a direct proof

To prove `P → Q`, assume `P` and derive `Q`. Each step must be justified by a
definition, a previous theorem, or an algebraic identity. The habit that
separates a proof from an argument is **naming the justification** at each
line.

Template:

```
Claim. If n is even then n² is even.
Proof. Assume n is even, so n = 2k for some integer k.
       Then n² = 4k² = 2(2k²), which is even.  ∎
```

Notice that the definition of "even" did all the work. Most failing proofs
are failing definitions, not failing logic.

## 2. Proof by contradiction

To prove `P`, assume `¬P` and derive `⊥` (a contradiction). To prove
`P → Q`, assume `P ∧ ¬Q` and derive `⊥`.

Template:

```
Claim. √2 is irrational.
Proof. Suppose √2 = p/q in lowest terms.
       Then 2q² = p², so p² is even, so p is even: p = 2m.
       Then 2q² = 4m², so q² = 2m², so q is even.
       But p and q were in lowest terms. Contradiction.  ∎
```

## 3. Contradiction versus contraposition

Both prove `P → Q`, but they are not the same move:

- Contraposition proves `¬Q → ¬P`. It is a *direct* proof of a different
  statement, and the result is constructive.
- Contradiction assumes `P ∧ ¬Q` and hunts for `⊥`.

Contraposition is usually cleaner when the negated conclusion is easy to
manipulate. Contradiction is unavoidable for results like irrationality and
infinitude of primes, where the conclusion has no positive algebraic form to
work with.

## 4. Common failure modes

1. **Circular reasoning** — using the claim, restated, as a step.
2. **Unjustified "clearly"** — a step that is the actual content of the proof.
3. **Proving the converse** — deriving `Q → P` while claiming `P → Q`.
4. **Negation errors** — assuming `¬(P ∧ Q)` and treating it as `¬P ∧ ¬Q`.
   The correct form is `¬P ∨ ¬Q`.
5. **Vacuous cases ignored** — division by zero, empty sets, empty domains.

## 5. Refutation is also a proof

To disprove `∀x. P(x)` you need one witness with `¬P(x)`. That is why
counterexample search is a legitimate verification activity, and why
ProofGarden reports violations as first-class results rather than errors.

`proofgarden modelcheck` returns `violated` plus a trace for exactly this
reason: the trace *is* the proof of the negated claim.

## 6. Exercises

1. Prove directly: the sum of two odd integers is even.
2. Prove by contraposition: if `n²` is odd then `n` is odd.
3. Prove by contradiction: there are infinitely many primes.
4. Find the error: "Suppose `a = b`. Then `a² = ab`, so `a² − b² = ab − b²`,
   so `(a−b)(a+b) = b(a−b)`, so `a + b = b`, so `a = 0`."
5. Render each step of exercise 4 as a propositional formula and locate the
   invalid implication.

## 7. Further reading

- Velleman, *How to Prove It*, chapters 1–3.
- Solow, *How to Read and Do Proofs*.
