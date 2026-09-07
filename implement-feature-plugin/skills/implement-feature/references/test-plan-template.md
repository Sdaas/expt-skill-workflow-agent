# Test plan: <feature name>

> Gate 2 outbox. Enumerates the tests that will PROVE the feature, and the thresholds
> the CODE-REVIEW gate enforces. Consumed by `test-writer` (what to write),
> `test-reviewer` (is it covered?), and `code-reviewer` (thresholds met?).

## Test inventory
Each test maps to an acceptance criterion or a boundary. Cover happy path, edge cases,
negative/error cases, and every boundary in the inventory.

| ID | Level (unit/api/e2e) | What it asserts | Traces to (AC# / boundary) |
|----|----------------------|-----------------|----------------------------|
| T1 | unit | … | AC1 |
| T2 | unit | edge: empty input → … | AC3 |
| T3 | api  | … | AC5 |
| T4 | e2e  | real flow: … | AC1, boundary: fs |

## Coverage target
- **Line/branch coverage ≥ <N>%** (`pytest-cov`). State the number and any justified
  exclusions.

## Mutation target
- **Mutation kill rate ≥ <M>%** (`mutmut`). Surviving mutants above this are treated as
  weak tests and block APPROVE at CODE-REVIEW.

## Concurrency plan (fill only if the feature is concurrent/async)
- If the boundary inventory flags threads / async I/O / shared mutable state: list the
  property-based / stress / async tests (`hypothesis`, `pytest-asyncio`, stress loops
  under `python -X dev`) and the concurrency review focus (races, deadlocks, ordering,
  cancellation).
- Otherwise: **"No concurrency surface — skipped."**
