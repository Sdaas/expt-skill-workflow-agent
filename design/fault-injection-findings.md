# Finding: Phase 4 fault-injection pass — feature resilient; a resiliency-review gap surfaced

**Date:** 2026-09-11 · **Branch:** `refactor/shippable-plugin` · **Status:** ✅ pass complete.

The second half of Phase 4's done-bar: inject network faults (timeouts, 5xx) against the async
`CachedFetcher` feature so the un-mocked VERIFY path, the resiliency review dimension, and the
concurrency policy are **genuinely exercised, not just asserted**. Feeds the Developer Guide's
**testing / dry-run methodology** and **design-principles** sections (Phase 3).

---

## 1. Mechanism (decided: `httpx.MockTransport`)

The feature's design exposes a transport injection seam — `CachedFetcher(transport=...)` — for
exactly this. Faults are injected through it deterministically, no network / no extra process:

- a handler that **raises** injects a transport-level fault (`httpx.ReadTimeout` /
  `httpx.ConnectTimeout`, raised *before* any response exists — so it propagates from
  `client.get()`, a different code path from `response.raise_for_status()`);
- a handler that **returns a 5xx `Response`** injects a server error;
- both are also driven under `asyncio.gather(...)` to exercise coalescing under fault.

Test module (run in-container fixture `~/test-implement-feature`):
`tests/test_fetch_json_faults.py` — 9 tests. A real-socket timeout was deliberately **not**
added: the feature exposes no timeout knob (configurable timeout is a documented non-goal — see
§3), so a real timeout would mean either a >5s hang on httpx's default (slow/flaky) or a feature
change out of scope. The MockTransport path exercises the full `CachedFetcher` exception /
coalescing / caching logic un-mocked (only the socket is simulated); the committed suite already
carries real-socket e2e for the 200 / 404 / malformed-body cases.

## 2. Result — the feature is genuinely resilient (no bug)

All 9 fault tests pass; full suite **64 passed, 100% line+branch coverage** retained; module is
ruff- + ruff-format- + mypy-clean. Verified behaviors against the real code:

| Fault injected | Observed behavior | ✓ |
|---|---|---|
| `ReadTimeout` / `ConnectTimeout` | propagates as the same `httpx` type (and as the umbrella `httpx.TimeoutException`); **not cached** — a retry issues a fresh request and can succeed | ✓ |
| 5xx spread (500 / 502 / 503 / 504) | each raises `httpx.HTTPStatusError` with the right status; **not cached**; uniform — not special-cased to 500 | ✓ |
| Timeout under 10 concurrent coalesced callers | **exactly one** real request; all ten observe the same fault; failure **not cached** (fresh call after) | ✓ |
| Coalesced timeout then recovery | first wave all time out (1 request), second wave issues one fresh request that succeeds and is shared | ✓ |

The `transport` injection seam and the request-coalescing implementation both hold under
transport-level faults. This is a positive validation of what the plugin produced.

## 3. The methodology gap this surfaced (the point of the exercise)

Reading the committed run's handoff
(`00-async-cached-json-fetcher-202609110808/handoff/`):

- **Requirements gate — correct.** `01-requirements.md` consciously scopes a **configurable
  timeout** *out* ("httpx's default timeout is used — no custom timeout parameter"; "configurable
  timeout" listed among non-goals). Good: the interview captured it as an explicit non-goal.
- **Test-plan + resiliency review — gap.** `04-test-plan.md` enumerates only **response-level**
  faults — non-2xx status (T4/T9/T14) and malformed body (T5/T15) — mocked and un-mocked. The
  boundary inventory names the network boundary but only for status/body outcomes.
  `08-code-review-findings.md` records the "six quality dimensions … fully assessed … no
  findings." **Transport-level faults — timeouts, connect failures — were never enumerated as a
  test case nor flagged by the resiliency dimension**, even though they are a real runtime fault
  path for any network call on the default timeout.

The run conflated **"no *configurable* timeout" (a correct scope decision)** with **"no need to
*test* timeout behavior at all" (a coverage gap)**. My fault-injection pass shows the code
happens to handle it correctly — so this is a **test-coverage / review-rubric gap, not a
correctness bug**.

## 4. Proposed plugin nudge (small, precise) — for decision

For any feature whose boundary inventory includes a **network** boundary, the resiliency review
dimension (and the test-plan template) should require **at least one transport-level fault test**
— a timeout / connection failure raised before a response — asserting it **propagates** and is
**not cached**, distinct from response-level (status / body) faults. Candidate touch-points:

- `skills/implement-feature/references/quality-standards.md` — resiliency dimension wording.
- `skills/implement-feature/references/test-plan-template.md` — a transport-fault row for network
  boundaries.
- `agents/test-writer.md` / `agents/code-reviewer.md` — one line so the rubric is applied.

**DECIDED (2026-09-11): fold into Phase 3** — apply this nudge to the touch-points above during
the DG rewrite (which edits these files anyway). Not an open question; a committed Phase 3 task.

## 5. Consequences

- Phase 4's fault-injection done-bar is **met**: faults injected, un-mocked feature logic
  exercised, concurrency-under-fault confirmed, evidence recorded.
- The feature needs **no fix**.
- Carry §3 (the transport-vs-response fault distinction) into the DG design-principles section as
  a real trap the dry run caught.
</content>
