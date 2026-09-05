# Design principles: change locality, DRY, KISS, YAGNI

## Optimize for change locality

- Keep code that changes for the same reason together and let unrelated responsibilities change independently.
- Make required collaborators and configuration explicit. Avoid hidden service locators, mutable global state, and circular dependencies.
- Isolate volatile external systems behind an owned boundary when they genuinely need to change or be tested independently.
- Introduce an interface, layer, or dependency inversion only for an observed substitution, testing, or independent-change boundary. Do not create an interface per class, a wrapper per dependency, or another layer merely to appear decoupled.
- Keep every subtype or implementation behaviorally substitutable for its advertised abstraction. Do not strengthen preconditions, weaken promised results, violate invariants, or introduce incompatible errors or side effects outside the contract. Add shared contract tests when multiple implementations create material risk.
- Shape interfaces around the capabilities their actual consumers use. Split an interface only when distinct consumers, permissions, or change patterns demonstrate a real boundary.

## Apply DRY to knowledge, not visual similarity

- Identify duplicated knowledge, business rules, intent, schemas, or invariants whose copies must change together. Ask: would one conceptual change require coordinated edits in these places? If not, do not force them behind one abstraction because the lines look similar.
- Put one authoritative representation in the module, function, type, schema, or configuration layer that owns the concept.
- Prefer a small function, module, or composed collaborator when it expresses the shared rule with low coupling. Use inheritance only for a genuine substitutable is-a relationship.
- Remove the old copies after callers use the authoritative implementation, then test every affected path.
- Do not create a premature or condition-heavy abstraction to satisfy DRY. A little independent code can be safer than coupling concepts that only happen to look alike. Abstract once the shared knowledge and ownership are clear.

## Apply KISS to the complete solution

- Choose the simplest design that fully meets the acceptance contract and existing constraints.
- Follow established project conventions unless they are the cause of the problem.
- Prefer direct control flow, clear names, narrow responsibilities, and explicit data movement.
- Remove dead paths, needless layers, clever indirection, and configuration with no current purpose.
- Keep required validation, error handling, security, observability, migration work, and tests. Necessary correctness is not complexity.
- Optimize for comprehension and change safety, not minimum line count.

## Apply YAGNI to speculative work

- Implement the current acceptance contract and the support it demonstrably needs now.
- Do not add hypothetical extension points, generic frameworks, future modes, unused configuration, speculative caching, or extra dependencies without a current consumer or measured need.
- Do not preserve unused scaffolding on the claim that it may become useful.
- Keep the refactoring and tests required to make the current change safe; YAGNI is not permission to leave fragile code.
- Record future ideas outside the implementation when they are not part of the accepted scope.

## Resolve conflicts in this order

1. Protect correctness, data, security, accepted contracts, and verified repair of defects.
2. Meet the current accepted requirement completely.
3. Preserve safe state transitions and side effects.
4. Preserve trust-boundary, error-integrity, and resource-safety requirements.
5. Keep authoritative operational and contract documentation accurate.
6. Prefer the simplest maintainable design with local change impact.
7. Remove proven duplication of knowledge without speculative abstraction.

Never use DRY to justify an abstraction that violates KISS or YAGNI. Never use KISS or YAGNI to omit work required for a correct, safe, verified solution.
