---
name: implement-feature
description: Interview-driven, test-first, human-in-the-loop workflow to build a Python feature. Use when the user wants to implement a new feature/capability with TDD, staged human approvals, isolated model-pinned review gates, and a committed result. Triggered by /implement-feature or a confirmed natural-language feature request.
---

# implement-feature — the conductor's score

You are the **conductor [C]**: the interactive session that holds the through-line,
talks to the human, and delegates bias-sensitive gates to **isolated subagents [I]**.
Walk the gates **in order**. Announce each gate as you enter it. Never let a
downstream gate see a prior gate's raw transcript — only the **curated handoff files**.

**Hard rule:** never commit before the human has reviewed and approved (Gate 9).

## Roles & the handoff contract

- **[C] conductor** — this session. Human-facing gates + orchestration.
- **[I] isolated subagent** — spawned via the Agent/Task tool as a named agent type,
  fresh context, pinned model/effort, sees ONLY its curated inbox. **Plugin agents are
  namespaced by the plugin name**, so the `subagent_type` is
  `implement-feature:test-writer`, `implement-feature:test-reviewer`,
  `implement-feature:implementer`, `implement-feature:verifier`,
  `implement-feature:code-reviewer` — never the bare name. (Verified empirically.)

**Workdir:** the feature's working directory `<workdir>` (agreed at Gate 0). Its
handoff store is `<workdir>/handoff/`. Pass the absolute `<workdir>` in every
subagent brief so each agent can resolve its inbox/outbox paths.

**Handoff files (each gate reads a curated inbox, writes a defined outbox):**

| Gate | Reads (inbox) | Writes (outbox) |
|---|---|---|
| WRITE-TESTS [I] | `requirements.md` + `design-interface.md` + `test-plan.md` (**never** `design-internal.md`) | `tests/…` + `test-intent.md` |
| TEST-REVIEW [I] | `requirements.md` + full design + tests + `test-intent.md` | `test-review-findings.md` |
| IMPLEMENT [I] | tests + full design | `src/…` |
| VERIFY [I] | `requirements.md` (ACs + boundary inventory) | `verify-report.md` |
| CODE-REVIEW [I] | `requirements.md` + full design + whole diff | `code-review-findings.md` |

The interface/internal design split (Gate 2) keeps the test-writer blind to the
algorithm. **Never hand `design-internal.md` to the test-writer.**

## Quality standards (single source of truth)

The toolchain, the Definition of "green", the coverage/mutation gates, and the
concurrency policy live in **`references/quality-standards.md`** (in this skill's
folder). Read it, and pass its **absolute path** to every subagent brief so each gate
applies the same standard. This workflow is **prescriptive about the dev container** —
it assumes the pinned toolchain from `toolchain/requirements-dev.txt` is installed.

## Observability & guardrails (enforced automatically)

Two records, plus a hard guard, run alongside every gate:

1. **Gate run-log (conductor-written).** Append one line to
   `<workdir>/handoff/run-log.jsonl` as each gate completes:
   `{gate, mode, agent, model, effort, inbox:[...], outbox:[...], result, ts}` — the
   orchestration story.
2. **Guard hook audit (automatic).** The plugin ships a **PreToolUse hook**
   (`hooks/hooks.json` → `hooks/scripts/guard.py`) that fires for the conductor **and
   every subagent**, appending `{ts, agent_type, agent_id, tool, target}` for every
   Read/Bash/Grep/Glob — a tamper-evident record of exactly what each agent read.
3. **Guard hook enforcement (automatic, verified).** The same hook **denies**:
   - reading `.env` / keys / credentials / ssh keys — for **any** agent (security
     guardrail);
   - reading `design-internal.md` — for the **test-writer** only (algorithm-blind), Read
     *and* Bash; and
   - Edit/Write to any **test file** — for the **implementer** only (test-integrity: it
     must pass the tests, not change them).
   Each is defense-in-depth with the agents' own role instructions.

The deterministic analyzer (built at the observability chunk) reads the hook audit
(stable source of reads) and cross-checks the session transcript for per-agent
**model + token** figures. See `../../../design/isolation-experiments.md` for the
validation of all of the above.

---

## Gate 0 — CLASSIFY + MODEL PLAN + PREFLIGHT  [C] ↔ human

0. **Preflight (hard-fail).** Confirm we are inside the dev container and run the tool
   check from `references/quality-standards.md`
   (`ruff --version && mypy --version && pytest --version && mutmut --version`). **If any
   tool is missing, STOP** and tell the human to rebuild/enter the dev container
   (`.devcontainer` postCreate installs `toolchain/requirements-dev.txt`). Do not proceed.
1. Restate the feature in **one sentence**.
2. Propose the **workdir** (where code + `handoff/` will live) and confirm the stack
   is **Python** (this workflow targets Python).
3. Present the **per-gate model/effort plan** below. The invariant: **design and every
   review use a higher model (or effort) than implementation.** The human may adjust
   any row.

   | Gate | Runs as | Model / effort | Why |
   |---|---|---|---|
   | INTERVIEW | [C] | Opus 4.8, high | requirements reasoning = strong model |
   | DESIGN / SPEC | [C] | Opus 4.8, high | design = strong model |
   | WRITE-TESTS | [I] `test-writer` | Sonnet, high | writing tests = implementation |
   | TEST-REVIEW | [I] `test-reviewer` | Opus 4.8, high | review > implementation |
   | IMPLEMENT | [I] `implementer` | Sonnet, high | implementation |
   | VERIFY | [I] `verifier` | Sonnet, high | verification |
   | CODE-REVIEW | [I] `code-reviewer` | Opus 4.8, high | review > implementation |
   | REVIEW-GUIDE / COMMIT | [C] | Sonnet or Haiku | mechanical presentation + commit |

   Model IDs: Opus 4.8 = `claude-opus-4-8`; Sonnet 5 = `claude-sonnet-5`;
   Haiku 4.5 = `claude-haiku-4-5-20251001`.

**STOP. Do not begin any work until the human confirms the workdir and the model plan.**
Record the confirmed plan into `<workdir>/handoff/run-log.jsonl` (first entries).

---

## Gate 1 — INTERVIEW  [C] ↔ human

Interview to full clarity using a **grilling** approach. Do NOT guess scope.

**Method (design tree, worked in rounds):**
- Map the feature as a tree of decisions. Each round, ask the whole **frontier** —
  every question whose prerequisites are already settled.
- Format each question numbered, with **your recommended answer**:
  ```
  ❓ **Q1** — **<title>**: <question, incl. options>
  ➡️ <your recommended answer>
  ```
- **Facts are your job; decisions are the human's.** If a question needs a fact from the
  environment (existing code, conventions, deps), dispatch a subagent to find it — don't
  ask the human what you can look up. A running lookup is an unsettled prerequisite: ask
  the rest of the frontier now, defer the questions downstream of it.
- Each answer reshapes the tree; recompute the frontier and ask the next round. Done when
  the frontier is empty — **nothing silently assumed**.

**You must reach explicit answers for all four buckets** (see
`references/requirements-template.md`):
1. **Functional ACs** — inputs/outputs, behavior, error conditions, edge cases.
2. **Non-functional ACs** — scale, performance, security (write "N/A — reason" if none).
3. **Constraints** — mandated/forbidden tech, libraries, patterns, style.
4. **Boundary inventory** — external boundaries (network/subprocess/fs/entrypoint/dep),
   each with how it will be exercised un-mocked at VERIFY. "None (pure feature)" is valid.

**Close the gate:**
- Summarize the four buckets back to the human.
- **STOP. Do not write `requirements.md` or proceed until the human replies APPROVED.**
- On approval, write `<workdir>/handoff/requirements.md` using
  `references/requirements-template.md`. Append the run-log entry.

## Gate 2 — DESIGN / SPEC  [C] ↔ human

Read `<workdir>/handoff/requirements.md`. Decide the solution's shape and write **three**
handoff files (use the templates in `references/`).

**The interface / internal split (the mechanism that keeps the test-writer blind, P15):**
- `<workdir>/handoff/design-interface.md` — the **public contract only** (signatures,
  types, I/O, observable error/edge behavior, invariants). **Shared** with the
  test-writer. Template: `references/design-interface-template.md`.
- `<workdir>/handoff/design-internal.md` — the **algorithm**, data structures,
  alternatives, complexity, quality expectations, risks. **Withheld** from the
  test-writer; seen by implementer + reviewers. Template:
  `references/design-internal-template.md`.
  **Rule: nothing that reveals the algorithm may leak into `design-interface.md`.**

**The test plan** (`<workdir>/handoff/test-plan.md`, template
`references/test-plan-template.md`) — consumed by test-writer, test-reviewer, and
code-reviewer:
- Enumerated tests (**unit / api / e2e**), each traced to an **AC or a boundary**;
  cover happy path, edges, negatives, and every boundary in the inventory.
- **Coverage threshold** and **mutation kill-rate threshold** (the numbers Gate 7
  enforces via `pytest-cov` / `mutmut`).
- If `requirements.md`'s boundary inventory flags the feature concurrent/async, the plan
  MUST include the property/stress/async tests + concurrency review focus (per
  `references/quality-standards.md`); otherwise state "No concurrency surface — skipped."

**Close the gate:**
- Present the approach + alternatives considered + the two design files + the test plan.
  (For a complex feature, optionally spawn a fresh design-review subagent first.)
- **STOP. Do not write the handoff files or proceed until the human replies APPROVED.**
- On approval, write the three files and append the run-log entry.

## Gate 3 — WRITE-TESTS  [I] `test-writer`

Delegate to the isolated, **algorithm-blind** test-writer. Do NOT write the tests
yourself, and do NOT coach it on the algorithm.

**Spawn it** via the Agent tool with `subagent_type: implement-feature:test-writer`
(namespaced by plugin; its model/effort/tools are pinned in `agents/test-writer.md`). The
brief you pass must contain ONLY:
- the absolute `<workdir>`;
- its inbox — read **`requirements.md` + `design-interface.md` + `test-plan.md`** and the
  standards file (`references/quality-standards.md`, by the path you resolve);
- the hard rule: **do NOT read `design-internal.md` or `src/`** — encode the contract,
  not an implementation;
- the task: implement the `test-plan.md` inventory under `<workdir>/tests/`, write
  `<workdir>/handoff/test-intent.md`, and confirm the suite is red.

**Exit condition (machine, not human):** the returned report must show the suite is
**RED for the right reason** — tests exist and fail because the implementation is
*absent*, not from import/collection/syntax errors. If it's red for the wrong reason,
re-spawn with the correction. When genuinely red, append the run-log entry and proceed.

*(This gate is re-entered from Gate 4 on CHANGES-REQUESTED — re-spawn the writer with the
findings file added to its inbox.)*

## Gate 4 — TEST-REVIEW  [I] `test-reviewer`

An **independent** critic reviews the tests **before** any implementation exists. Spawn a
**different** agent than the writer — `subagent_type: implement-feature:test-reviewer`
(Opus/high per the model plan; read-only, pinned in `agents/test-reviewer.md`).

**Its inbox (it sees more than the writer):** `requirements.md`, the **full** design
(`design-interface.md` **and** `design-internal.md`), `test-plan.md`, the tests, and
`test-intent.md`. (Only the *writer* is algorithm-blind; the reviewer is not.)

**It must judge:**
- **Intent match** — does each test assert the requirement, or only a proxy?
- **Non-tautology** — *would a wrong implementation still pass?* Do a mutation-minded
  analysis: name plausible bugs and confirm a test kills each.
- **Coverage** — every acceptance criterion and every boundary in the inventory, per the
  test plan (incl. the mutation cases behind the kill-rate target).
- **No implementation leakage** — tests encode the contract, not one algorithm.

It writes `<workdir>/handoff/test-review-findings.md` with a **verdict**:
- **CHANGES-REQUESTED → bounded loop:** re-spawn `implement-feature:test-writer` with the
  findings file added to its inbox; then re-review. **Bound it:** after 2 rounds with no
  progress, STOP and surface to the human.
- **APPROVE →** append the run-log entry and proceed.

The reviewer does **not** edit the tests (read-only) — it only reports; the writer makes
the changes on the next loop.

## Gate 5 — IMPLEMENT  [I] `implementer`  (inner loop)

Delegate to `subagent_type: implement-feature:implementer` (Sonnet/high; has
Write/Edit/Bash, pinned in `agents/implementer.md`). Its inbox is the **tests** + the
**full** design (`design-interface.md` + `design-internal.md`) + the standards file.

**Inner loop (machine condition, no human):**
1. Write the **minimum** implementation under `<workdir>/src/` per the design; honor the
   constraints in `requirements.md`.
2. Run the **fast checks** until all pass — **"green" = `pytest` passes AND `ruff` clean
   AND `mypy` clean** (per `references/quality-standards.md`).
3. Refactor while keeping green.

**Load-bearing rule: make the code pass the tests — NEVER weaken or edit the tests to
pass.** The tests are the approved, independently-reviewed contract (Gates 3–4). Enforced
in depth: (a) the **guard hook denies the implementer any Edit/Write to a test file**
(keyed on `agent_type`, same mechanism as the algorithm-blind rule); (b) this prose rule;
(c) the whole-diff CODE-REVIEW (Gate 7), which flags any change under `tests/`.

Exit when green; append the run-log entry, then proceed to VERIFY. (Coverage + mutation
are the slow checks, enforced at CODE-REVIEW — not here.)

## Gate 6 — VERIFY  [I] `verifier`  (outer loop)

**Green unit tests are not Done.** Spawn a **fresh, read-only** verifier —
`subagent_type: implement-feature:verifier` (Sonnet/high; observes, cannot fix — pinned in
`agents/verifier.md`). It did not write the code, so it won't drive it the way the author
expects. Its inbox: `requirements.md` (the ACs + boundary inventory) and `src/` (to invoke
the real thing, not to trust it).

**It must:**
1. For **each acceptance criterion**, invoke the **real** public function/flow and confirm
   the **observed** result matches — not just that a test is green.
2. For **every external boundary** in the inventory, exercise it **un-mocked** at least
   once (a mocked test only proved the mock). If the inventory is "None (pure feature)",
   verify on the acceptance examples and say so.
3. If `requirements.md` flagged concurrency, run the stress/property checks per
   `references/quality-standards.md`.

It writes `<workdir>/handoff/verify-report.md`: per-AC **observed** PASS/FAIL with the
actual value, the boundary drives performed, and an overall verdict.

**This is the OUTER loop.** On any FAIL → go **back to IMPLEMENT (Gate 5)** — re-enter the
inner loop, fix, re-green, then re-VERIFY (bounded; surface to the human if it won't
converge). On all-PASS → append the run-log entry and proceed to CODE-REVIEW.

## Gate 7 — CODE-REVIEW + quality  [I] `code-reviewer`  (the last unattended gate)

Spawn a fresh, read-only whole-diff reviewer —
`subagent_type: implement-feature:code-reviewer` (Opus/high; pinned in
`agents/code-reviewer.md`). "One senior engineer reviewing the entire PR": fresh context
kills anchoring, a stronger model than the implementer kills monoculture. Its inbox:
`requirements.md` + the full design + the **whole change** (tests + `src/`) + the standards.

**It reviews across six quality dimensions** (borrowed from the `claude-sdlc` profile
backbone — scale each to the feature; state **`N/A — why`**, never silently drop one):
1. **Best practices** — modularity/cohesion, purity/side-effects, naming, typing, docstrings;
   idiomatic Python; the constraints in `requirements.md` honored.
2. **Performance & scale** — the measurable signals the design flagged; no accidental
   O(n²)/N+1 or unbounded growth.
3. **Testing pyramid** — the **slow checks** live here (deferred by split-by-speed):
   **coverage** (`pytest --cov=src`) and **mutation** (`mutmut run` → kill-rate) vs the
   `test-plan.md` thresholds. Surviving mutants = weak tests; call out untested lines.
4. **Security** — injection/quoting, secrets, filesystem, dependency surface.
5. **Reliability & resilience** — timeout/retry/backoff/idempotency at every boundary in the
   inventory; concurrency (races/deadlocks/ordering/cancellation) if `requirements.md` flagged it.
6. **Observability & logging** — the change is diagnosable (levels, messages) per policy.

Plus two cross-cutting checks: **whole-diff consistency** (no dead/speculative code) and
**test-integrity** (flag **any change under `tests/`** — the implementer must not have altered
them). Fast checks (`ruff`/`mypy`/unit `pytest`) were gated in IMPLEMENT — confirm they still
pass; spend the effort on the six dimensions + the slow checks.

It writes `<workdir>/handoff/code-review-findings.md` with **every finding TYPED with a repair
target**, and a **verdict**:
- **APPROVE →** append the run-log entry and proceed to the human gates (8–10).
- **CHANGES-REQUESTED → route each finding by its type (one review pass, two repair paths — P37):**
  - **`→IMPLEMENT`** — *code* defects (correctness, best-practice, reliability/perf,
    observability wiring, **dead-code deletion**) → back to **IMPLEMENT (Gate 5)**; the
    implementer edits `src/` only.
  - **`→TESTS`** — *weak/missing tests* (surviving mutants, coverage gaps that are missing
    tests) → back to **WRITE-TESTS (Gate 3)** then **TEST-REVIEW (Gate 4)**. New tests must
    themselves be independently reviewed before re-use — the implementer is **barred** from
    editing tests (guard-hook job #4), so routing a test-weakness to IMPLEMENT is a dead end.
    A surviving mutant that is actually *unreachable-by-requirement code* routes `→IMPLEMENT`
    to delete it instead.

Findings of both types in one round dispatch to both actors. After repair, re-converge forward
(→ VERIFY → CODE-REVIEW). **Bound the loop; surface to the human if it won't converge.**

## Gate 8 — REVIEW-GUIDE  [C]  (Sonnet/Haiku)

Make the human's review fast and focused — **guide the eye; do not dump a diff.** Present:
- the list of **changed files**, with a recommended **review order**;
- **one line per file** — why it matters / where the key change is;
- **pointers to every findings file**: `handoff/test-review-findings.md`,
  `handoff/verify-report.md`, `handoff/code-review-findings.md`, and the audit
  `handoff/run-log.jsonl` (what each agent did, which model, what it read).

The observability from every gate pays off here: the human can drill into any agent's work
rather than re-reviewing everything from scratch.

## Gate 9 — HUMAN REVIEW  [C] ↔ human   (approval gate — the ship decision)

**STOP. Do not commit. Wait for the human to review and reply APPROVED.** If the human
requests changes, route them to the relevant gate (e.g. a logic fix → IMPLEMENT; a missing
test → back through WRITE-TESTS/TEST-REVIEW), then re-run forward and re-present at Gate 8.
The human owns the decision to ship — nothing here is automatic.

## Gate 10 — COMMIT  [C]  (Sonnet/Haiku)

**Only after the human replied APPROVED** (the hard rule from Gate 0): commit the change
with a clear message referencing the feature and its acceptance criteria. Authorship is
**Soumendra Daas / soumendra.daas@gmail.com**. This is the **only** gate that writes to git
history. (In a repo with branch/PR conventions: commit on the feature branch, push — the
pre-push hook runs the tests — and open a PR; merge only on green CI + approval.)

Append the final run-log entry. The pipeline (Gates 0–10) is complete.

---

## Rules
- Curated handoffs only — a gate never sees a prior gate's raw transcript.
- The test-writer is blind to `design-internal.md`.
- Design & every review use a higher model/effort than implementation.
- Not Done on green tests alone — VERIFY observed behavior.
- Bound every automated loop; surface to the human on no progress.
- Review before commit.
