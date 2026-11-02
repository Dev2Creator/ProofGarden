# Lesson 5 — Sets: Operations and Identities

## 1. What a set is

A set is a collection of distinct objects. `{1, 2, 3}` and `{3, 2, 1}` are the
same set; `{1, 1, 2}` is `{1, 2}`. Membership is written `x ∈ A`.

Two sets are equal exactly when they have the same members:

```
A = B  ⟺  ∀x. (x ∈ A ↔ x ∈ B)
```

This **extensionality** principle is what makes proofs about sets possible: to
prove `A = B` you prove two inclusions.

## 2. The operations

| Operation | Definition | Intuition |
| --- | --- | --- |
| `A ∪ B` | `{x : x ∈ A ∨ x ∈ B}` | either |
| `A ∩ B` | `{x : x ∈ A ∧ x ∈ B}` | both |
| `A \ B` | `{x : x ∈ A ∧ x ∉ B}` | in A, not in B |
| `Aᶜ` | `{x ∈ U : x ∉ A}` | complement in universe U |
| `A ⊆ B` | `∀x. (x ∈ A → x ∈ B)` | subset |
| `A × B` | `{(a, b) : a ∈ A ∧ b ∈ B}` | ordered pairs |
| `𝒫(A)` | `{S : S ⊆ A}` | all subsets |

`A × B` is ordered: `(1, 2) ≠ (2, 1)`. `A × B` has `|A| · |B|` elements, and
`|𝒫(A)| = 2^|A|`.

## 3. Algebraic laws, with intuition

Union and intersection are duals of each other:

```
A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)      distributivity
A ∩ (B ∪ C) = (A ∩ B) ∪ (A ∩ C)      distributivity
A \ (B ∪ C) = (A \ B) ∩ (A \ C)      De Morgan
A \ (B ∩ C) = (A \ B) ∪ (A \ C)      De Morgan
```

Notice the pattern: swapping `∪` with `∩` and `∪` with `∩` preserves truth.
This duality is the set-level version of the De Morgan laws in lesson 1.

## 4. Proof template: two inclusions

Claim: `A \ (B ∪ C) = (A \ B) ∩ (A \ C)`.

```
(⊆) Let x ∈ A \ (B ∪ C).
    Then x ∈ A and x ∉ B ∪ C.
    So x ∉ B and x ∉ C.
    Hence x ∈ A \ B and x ∈ A \ C,
    i.e. x ∈ (A \ B) ∩ (A \ C).

(⊇) Let x ∈ (A \ B) ∩ (A \ C).
    Then x ∈ A \ B, so x ∈ A and x ∉ B,
    and x ∈ A \ C, so x ∉ C.
    Thus x ∈ A and x ∉ B ∪ C,
    i.e. x ∈ A \ (B ∪ C).  ∎
```

Every element-level set proof has this shape. Write it out; do not skip to
the conclusion.

## 5. Indexed families

`⋃ᵢ∈I Aᵢ` and `⋂ᵢ∈I Aᵢ` generalise union and intersection over an index set.
For `I = ∅`, `⋃ᵢ∈∅ Aᵢ = ∅` while `⋂ᵢ∈∅ Aᵢ = U`. The empty intersection is the
whole universe, which surprises almost everyone once.

## 6. Exercises

1. Prove `A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)` with a two-inclusion proof.
2. Prove `A ⊆ B` implies `𝒫(A) ⊆ 𝒫(B)`.
3. Show `(A × B) ∪ (C × D) ⊆ (A ∪ C) × (B ∪ D)`, and give an example showing
   the reverse inclusion fails.
4. How many elements does `𝒫(∅)` have? How many does `𝒫(𝒫(∅))` have?

## 7. Further reading

- Halmos, *Naive Set Theory*, chapters 1–6.
- Velleman, *How to Prove It*, chapter 4.
