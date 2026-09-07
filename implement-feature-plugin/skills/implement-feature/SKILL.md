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
     guardrail); and
   - reading `design-internal.md` — for the **test-writer** only (algorithm-blind), Read
     *and* Bash. This is defense-in-depth with the test-writer's own role instructions.

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

## Gate 4 — TEST-REVIEW  [I] `test-reviewer`   *(fleshed in Chunk 14)*
Fresh reviewer checks the tests encode the ACs, are non-tautological, cover the
boundary inventory + mutation cases. **APPROVE →** proceed; **CHANGES-REQUESTED →**
re-spawn `test-writer` with findings (bounded: stop after 2 no-progress rounds).

## Gate 5 — IMPLEMENT  [I] `implementer`  (inner loop)   *(fleshed in Chunk 15)*
Minimum code to pass. **"Green" = `pytest` passes AND `ruff` clean AND `mypy` clean**
(fast checks, per `references/quality-standards.md`). Loop until green; refactor keeping
green. (Coverage + mutation are the slow checks, enforced at CODE-REVIEW.)

## Gate 6 — VERIFY  [I] `verifier`  (outer loop)   *(fleshed in Chunk 16)*
Drive the **real** feature on each AC; exercise every boundary **un-mocked** once.
Defect → back to IMPLEMENT.

## Gate 7 — CODE-REVIEW + quality  [I] `code-reviewer`   *(fleshed in Chunk 17)*
Whole-diff review + the **slow checks**: **coverage** (`pytest-cov`) and **mutation
kill rate** (`mutmut`) vs the thresholds in the test plan; for concurrent features, a
concurrency-focused review item. **CHANGES-REQUESTED →** back to IMPLEMENT (bounded).
**APPROVE →** proceed.

## Gate 8 — REVIEW-GUIDE  [C]   *(fleshed in Chunk 18)*
Present changed files, a recommended review order, one line per file, + pointers to
each findings file.

## Gate 9 — HUMAN REVIEW  [C] ↔ human   *(fleshed in Chunk 18)*
**STOP. Wait for the human to review and reply APPROVED.** Address changes; re-present.

## Gate 10 — COMMIT  [C]   *(fleshed in Chunk 18)*
After approval: commit with a clear message. (Authorship: Soumendra Daas /
soumendra.daas@gmail.com.)

---

## Rules
- Curated handoffs only — a gate never sees a prior gate's raw transcript.
- The test-writer is blind to `design-internal.md`.
- Design & every review use a higher model/effort than implementation.
- Not Done on green tests alone — VERIFY observed behavior.
- Bound every automated loop; surface to the human on no progress.
- Review before commit.
