# Lesson 3 — Predicate Logic: Predicates and Quantifiers

## 1. Why propositional logic is not enough

Consider: "every student who passes the exam graduates". Propositional logic
can only name this whole sentence `P`. It cannot express *why* it is true,
cannot separate the subject from the property, and cannot reason about
individuals at all.

Predicate logic adds three things: **objects**, **predicates** (properties of
objects), and **quantifiers** (how many objects have a property).

## 2. The vocabulary

| Symbol | Meaning | Example |
| --- | --- | --- |
| `Student(x)` | a predicate, true of x | `Student(priya)` |
| `Passes(x)` | another predicate | `Passes(priya)` |
| `∀x. P(x)` | for all x, P(x) holds | `∀x. Student(x) → Passes(x)` |
| `∃x. P(x)` | there exists an x with P(x) | `∃x. Student(x) ∧ Fails(x)` |

The **domain of discourse** is the collection of objects quantified over. The
same sentence changes meaning with a different domain: over all humans,
`∀x. Mortal(x)` is false; over all living things it is still false (rocks
exist); over all animals it is plausibly true.

## 3. The two most common translation errors

**Error 1 — using ∧ with ∀.**
`∀x. Student(x) ∧ Passes(x)` says *everything in the domain is a passing
student*. That is almost never what "all students pass" means. Correct:
`∀x. Student(x) → Passes(x)`.

**Error 2 — using → with ∃.**
`∃x. Student(x) → Passes(x)` is satisfied by any domain containing one
non-student, because `false → anything` is true. Correct:
`∃x. Student(x) ∧ Passes(x)`.

Rule of thumb: **∀ pairs with →, ∃ pairs with ∧.**

## 4. Mixed quantifiers do not commute

Assume the domain is people, `Loves(x, y)` means "x loves y".

- `∀x. ∃y. Loves(x, y)` — everyone loves somebody (possibly different people).
- `∃y. ∀x. Loves(x, y)` — there is one person loved by everybody.

The second is much stronger. Order matters whenever different quantifiers are
mixed.

## 5. Exercises

1. Translate: "no student fails every exam."
2. Translate: "some exam is failed by every student."
3. Are the two sentences in exercise 1 and 2 related? Which implies which?
4. Give a domain of two objects where `∃y. ∀x. Loves(x, y)` is true and
   `∀x. ∃y. Loves(x, y)` is false. Then swap the domain.

## 6. What this release can and cannot check

The ProofGarden engine in `proofgarden/logic` handles **propositional** formulas
only. Predicate logic reasoning requires either a theorem prover or finite
model enumeration, which is deliberately out of scope for v0.2 — see
`docs/limitations.md`. These lessons are study material, not executable
checks, and the roadmap records the gap.

## 7. Further reading

- Enderton, *A Mathematical Introduction to Logic*, chapter 2.
- van Dalen, *Logic and Structure*, chapter 3.
