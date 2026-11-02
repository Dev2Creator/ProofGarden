# Lesson 6 — Relations and Equivalence

## 1. A relation is a set of pairs

A **binary relation** on `A` is a subset `R ⊆ A × A`. We write `a R b` for
`(a, b) ∈ R`.

Example: on `{1, 2, 3}`, the relation `<` is `{(1,2), (1,3), (2,3)}`.

## 2. The four classic properties

| Property | Definition |
| --- | --- |
| reflexive | `∀a. a R a` |
| symmetric | `∀a,b. a R b → b R a` |
| antisymmetric | `∀a,b. (a R b ∧ b R a) → a = b` |
| transitive | `∀a,b,c. (a R b ∧ b R c) → a R c` |

## 3. Equivalence relations

A relation that is reflexive, symmetric, and transitive is an **equivalence
relation**. Its defining power is that it **partitions** the set.

Example: on integers, `a ≡ b (mod 3)` iff `a − b` is divisible by 3. The
partition is `{…, −3, 0, 3, …}`, `{…, −2, 1, 4, …}`, `{…, −1, 2, 5, …}`. These
classes are the elements of `ℤ/3ℤ`.

Key theorem: every equivalence relation induces a partition into equivalence
classes, and every partition induces an equivalence relation. The two notions
are interchangeable.

Why it matters for verification: **quotienting** by an equivalence relation is
how state abstraction works. If two concrete states behave identically under
every transition, the checker may explore one representative instead of both.
That is exactly the soundness argument used by symmetry reduction and
bisimulation minimisation — topics in the formal-methods track.

## 4. Partial orders

A relation that is reflexive, antisymmetric, and transitive is a **partial
order**. Examples: `⊆` on sets, `≤` on numbers, divisibility on positive
integers.

A partial order is **total** if any two elements are comparable. `≤` on `ℕ`
is total; `⊆` on `𝒫({1,2})` is not (`{1}` and `{2}` are incomparable).

Partial orders give the vocabulary for progress and termination arguments:
a program measure decreases along a well-founded order.

## 5. Checking properties mechanically

`proofgarden.state` models transitions between states, and reachability is a
relation on states. You can therefore use the explorer to test relational
properties of small systems:

1. Build a `StateSystem` whose transitions are the relation.
2. Check reachability of specific pairs to test symmetry or transitivity
   witnesses.
3. Use invariant checks as counterexample finders for "is this relation
   antisymmetric?" — a forbidden pattern is any pair `(a, b)` and `(b, a)` with
   `a ≠ b`.

This is test-by-witness, not proof. `docs/limitations.md` says the same thing
in more detail.

## 6. Exercises

1. Show `|` (divisibility) on positive integers is a partial order but not
   total.
2. Is `a R b` iff `|a − b| ≤ 1` on integers an equivalence relation? Prove or
   give a counterexample for each property.
3. Prove that an equivalence relation's classes are disjoint.
4. Give a two-element model where a relation is symmetric and transitive but
   not reflexive, and explain why the failure is vacuous or real.

## 7. Further reading

- Velleman, *How to Prove It*, chapter 4.
- Rosen, *Discrete Mathematics*, chapter 9.
