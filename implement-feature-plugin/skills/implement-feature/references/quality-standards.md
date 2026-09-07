# Quality standards — the workflow's Definition of Done

> Single source of truth (T12). The conductor passes this file's absolute path to
> each agent's brief; agents apply it rather than restating it. To raise the bar,
> edit **this file** — not the individual gates or agents.

## Environment assumption
This workflow is **prescriptive about the dev container**: it runs inside the project
dev container (see `.devcontainer/`), where the pinned toolchain
(`implement-feature-plugin/toolchain/requirements-dev.txt`) is installed. It is not
supported to run on a bare host.

## Toolchain (pinned in the container)
| Tool | Purpose | Command |
|------|---------|---------|
| ruff | lint + format | `ruff check .` and `ruff format --check .` |
| mypy | static type checking | `mypy src/` |
| pytest | tests | `python -m pytest -q` |
| pytest-cov | coverage | `python -m pytest --cov=src --cov-report=term-missing` |
| mutmut | mutation testing | `mutmut run` then `mutmut results` |
| hypothesis / pytest-asyncio | property/stress/async (situational) | via the test files |

## Gate 0 preflight (hard-fail)
Before any work, the conductor verifies the environment. **If any check fails, STOP and
tell the human to rebuild/enter the dev container — do not proceed.**
```
ruff --version && mypy --version && pytest --version && mutmut --version
```
(Also confirm we are inside the container, not the host.)

## Definition of "green" — IMPLEMENT inner loop (fast checks)
The implementer may NOT exit its loop until ALL of:
1. `python -m pytest -q` — all tests pass.
2. `ruff check .` — clean (and `ruff format --check .`).
3. `mypy src/` — no type errors.

## CODE-REVIEW gate (slow checks) — thresholds live in the per-feature test plan
- **Coverage** ≥ the threshold set in `handoff/` test plan (`pytest-cov`).
- **Mutation kill rate** ≥ the threshold set in the test plan (`mutmut`); surviving
  mutants are reported as weak tests.

## Concurrency policy (situational — driven by the boundary inventory)
- If the feature is concurrent/async (threads, async I/O, shared mutable state), the
  Gate 2 **test plan MUST** include property-based + stress tests (`hypothesis`,
  `pytest-asyncio`, stress loops run under `python -X dev` with `faulthandler`), and
  CODE-REVIEW MUST include a concurrency-focused review item (races, deadlocks,
  ordering, cancellation).
- If the feature is not concurrent, state that once ("no concurrency surface") and skip
  — same shape as a VERIFY skip.

## Best-practices the reviews enforce
Modularity/cohesion · purity / minimal side-effects · clear naming · full type
annotations · docstrings on public surface · honor the constraints in `requirements.md`.
