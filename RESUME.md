# RESUME — Tutorial Progress Tracker

> To continue in a new session: open this file and say **"read RESUME.md and continue."**

## How this tutorial works
Chunked tutorial (~200–250 words each) + hands-on build. Teach a chunk → comprehension
check → advance only when the user says "next." See `PLAN.md` for the full 17-chunk plan,
`TUTORIAL.md` for the accumulating concept reference, and `PATTERNS.md` for the running
design-patterns/anti-patterns/traps checklist we apply when building.

## Standing instructions (apply every session)
1. **Pacing:** teach one chunk → comprehension check → advance only on the user's "next."
2. **Doc-update timing:** update `RESUME.md` / `TUTORIAL.md` / `PATTERNS.md` **only** when the
   user says "next" (advances), never mid-chunk.
3. **Capture questions:** whenever the user asks a question mid-chunk, add a condensed Q&A of it
   (and the answer) into `TUTORIAL.md` at the next advance.
4. **Patterns checklist:** keep capturing design patterns / anti-patterns / traps in `PATTERNS.md`
   as they arise — the checklist we'll apply when building the toy and the real solution.
5. **Files:** deliverables under this folder; temp files in `/tmp/` or `*.tmp`, deleted when done.
6. **Commit per chunk:** on each advance ("next"), after recording the docs, **commit all of that
   chunk's changes** (one commit per chunk) before starting the next chunk. Never carry more than the
   current chunk's work uncommitted. (Instruction added 2026-09-07.)

## Status
- **Current phase:** Part D — Build the real product
- **Last completed chunk:** Chunk 15 ✅ (2026-09-07) — fleshed **Gate 5 IMPLEMENT**: the isolated
  `implement-feature:implementer` (Sonnet/high, sees full design + tests), inner loop until
  green = pytest + ruff + mypy; never weaken the tests. Extended the guard hook with a **4th job**:
  deny the implementer any Edit/Write to test files (test-integrity), unit-tested + regressions pass.
  Three-layer test integrity (hook + rule + code-review).
- **Next chunk to deliver:** Chunk 16 (Part D) — flesh **Gate 6 VERIFY**: outer loop; drive the real
  feature on each AC + exercise every boundary un-mocked; defect → back to IMPLEMENT.
- **Awaiting from user:** delivering Chunk 16 now (user said "continue").

## Resuming the container next session (quick ref)
1. `cd /Users/sdaas/dev/expt-skill-wotkflow-agent`
2. `devcontainer up --workspace-folder .`  (fast — image cached; container recreated if removed)
3. `devcontainer exec --workspace-folder . claude`  (login persists via the volume; usually no re-login)
4. The `toy-local-marketplace` + `toy-greet` install persist in the `~/.claude` volume; if
   `/toy-greet:greet` isn't present, re-run `claude plugin install toy-greet@toy-local-marketplace`
   then `/reload-plugins`. See `DEVCONTAINER.md` for full lifecycle.

## Progress log
- 2026-09-06 — Plan approved. Created `PLAN.md`, `RESUME.md`, `TUTORIAL.md`.
- 2026-09-06 — Delivered Chunk 1 (four building blocks).
- 2026-09-06 — Delivered Chunk 2 (anatomy of a skill).
- 2026-09-06 — Delivered Chunk 3 (subagents). Added `PATTERNS.md` running checklist per user request.
- 2026-09-06 — Delivered Chunk 4 (workflow pattern & gates). Added P6–P9, T3 to PATTERNS.md.
- 2026-09-06 — Delivered Chunk 5 (plugin packaging) + manifest Q&A. Recorded standing instructions.
- 2026-09-06 — Chunk 6 (toy build): created `toy-greet-plugin/` (plugin.json + commands/greet.md).
- 2026-09-06 — Fixed authorship to Soumendra Daas / soumendra.daas@gmail.com (memory + files).
- 2026-09-06 — Decided testing strategy: dev-container sandbox (see Key decisions). Captured dev-flow
  Q&As into TUTORIAL.md; added P10/T4 to PATTERNS.md. Revised PLAN (Part B, 18 chunks).
- 2026-09-07 — Chunk 7: built dev-container sandbox (Option A, devcontainer CLI, features), mirroring
  `~/dev/hello-dev-container`. Added `.devcontainer/`, `DEVCONTAINER.md`, repo-root `README.md`,
  `.gitignore`. Captured devcontainer Q&A + P11 in TUTORIAL/PATTERNS. `git init` + first commit.
- 2026-09-07 — Chunk 15 ✅ (build): fleshed Gate 5 IMPLEMENT in `SKILL.md` (Sonnet implementer, full
  design + tests inbox, inner loop to green=pytest+ruff+mypy, never weaken tests). Extended guard hook
  (job #4: implementer denied Edit/Write on test files; matcher now includes Edit|Write; unit-tested).
  Added P33. Committed.
- 2026-09-07 — Chunk 14 ✅ (build): fleshed Gate 4 TEST-REVIEW in `SKILL.md` — independent, read-only,
  higher-model critic; runs before implement; asymmetric inbox (sees full design); bounded loop back to
  the writer. Added P32 (asymmetric inboxes). Committed.
- 2026-09-07 — Chunk 13 ✅ (build + deviation): fleshed Gate 3 WRITE-TESTS; then ran an isolation
  investigation (user-driven, important). Stage 0 facts via `claude-code-guide`; Stage 1 local probes
  (proved model routing + tool hard-block + transcript read-audit; built `scratchpad/parse_transcript.py`);
  sandbox E5/E6 (plugin agents install + are **namespaced**; `blockReadsOutsideWorkingDirectories`
  fences Read+Bash; a **project** hook did NOT fire headless). User chose the most rigorous posture →
  built + validated a **plugin PreToolUse guard hook** (fires for subagents in headless; `agent_type`
  drives per-agent denial; secrets/.env denied for all; unit-tested). Deliverables:
  `implement-feature-plugin/hooks/*`, `design/isolation-experiments.md`, root `LAUNCHING-SUBAGENTS.md`.
  Docs updated (P28–P31, T15 resolved).
- 2026-09-07 — Chunk 12 ✅ (build): fleshed Gate 2 DESIGN/SPEC in `SKILL.md` (interface/internal
  split, 3-file outbox, test plan w/ coverage+mutation thresholds + concurrency mandate, STOP-until-
  APPROVED). Added `references/{design-interface,design-internal,test-plan}-template.md`. Clarified why
  thresholds live per-feature in the test plan (P24) not in the shared code-reviewer agent, and why
  design records rejected alternatives (ADR). Added P27 to PATTERNS. Committed (commit-per-chunk rule).
- 2026-09-07 — Chunk 11 ✅ (build): fleshed Gate 1 INTERVIEW in `SKILL.md` + added
  `references/requirements-template.md` (6-section artifact). Method = borrowed grilling engine
  (design tree, rounds, frontier, numbered Qs w/ recommended answers, facts-via-subagent) wrapped with
  a required 4-bucket schema + STOP-until-APPROVED + outbox write. Captured the grilling-vs-`grilling`
  comparison Q&A into TUTORIAL. Added P26/T16 to PATTERNS.
- 2026-09-07 — Chunk 10 ✅ (build): scaffolded `implement-feature-plugin/` (plugin.json, thin command,
  `skills/implement-feature/SKILL.md` conductor score, 5 agent-def files under `agents/`). Grounded the
  agent frontmatter (`model`/`effort`/`tools`/`disallowedTools`) in the user's `claude-sdlc` agent
  files. After user Qs, added the quality dimension: `toolchain/requirements-dev.txt` (pinned
  ruff/mypy/pytest/pytest-cov/mutmut/hypothesis/pytest-asyncio), `references/quality-standards.md`
  (Definition of Done), `.devcontainer` postCreate installs them, Gate 0 preflight hard-fails if a tool
  is missing. Placement = split by speed. Type checker = mypy (production CI-gate choice). Two items to
  verify in-sandbox: plugin agent namespacing/discovery, and effort honored for plugin agents.
- 2026-09-07 — Chunk 9 ✅ (design): re-designed `/implement-feature` as an 11-gate conductor +
  isolated-gate system. Research: read the `grilling` skill (borrowed its design-tree/round interview
  pattern), `/sdlc-feature` v1, and the user's `claude-sdlc` `feature-as-workflow` WIP
  (`/sdlc-feature-v2` + `design/gate-isolation-prototype.md`, already A/B-validated). Folded in:
  interface/internal design split, TEST-REVIEW gate, model-plan-at-CLASSIFY, agent-def files for
  effort pinning, VERIFY-observed, curated inbox/outbox contract. User additions: interview captures
  tech **constraints**; new **observability/analysis** capability (run-log + transcript-parsing Python
  analyzer; preventive+detective isolation). Updated PLAN (Part C done, Part D re-planned to 10–21,
  added observability section), TUTORIAL (Chunk 9 + 3 Q&As), PATTERNS (P13–P20, T10–T13). Kept as a
  from-scratch teaching build separate from `claude-sdlc`.
- 2026-09-07 — Chunk 8 ✅: `claude-code-guide` verified marketplace schema + commands. Added
  `.claude-plugin/marketplace.json`. In-container: `devcontainer up` (Claude Code 2.1.260), login,
  `/plugin marketplace add`, `claude plugin install toy-greet@toy-local-marketplace`, `/reload-plugins`,
  ran `/toy-greet:greet` — both gates fired. Captured Chunk 8 + add-vs-install Q&A + namespacing
  correction (P12/T8/T9). Committed. Session paused.

## Key decisions
- **`/implement-feature` = 11-gate conductor + isolated-gate design** (Chunk 9, 2026-09-07). See the
  table in `PLAN.md`. Borrows heavily from the user's validated `claude-sdlc` `/sdlc-feature-v2`
  prototype but stays a **separate from-scratch teaching build**. Includes an observability/analysis
  capability (the analyzer is deterministic Python — measurement, not orchestration, so "driverless"
  holds). Per-gate models pinned via `.claude/agents/*.md`; invariant: review > implementation.
- **Reference:** the design lineage lives in `~/dev/claude-sdlc`, branch `feature-as-workflow` —
  `design/gate-isolation-prototype.md` (decisions D1–D10, A/B results) + the untracked
  `.claude/commands/sdlc-feature-v2.md`. Read those to recall *why* each gate exists.
- Toy first → then real product.
- Build from scratch; do not dissect existing installed skills.
- Solid foundations before writing files.
- Target code language: Python.
- **Testing strategy = dev-container sandbox** (decided 2026-09-06; refined 2026-09-07 to Option A).
  Test the plugin inside a Docker dev container with its own isolated `~/.claude`; never install
  into the host global `~/.claude`.
  - Interactive Claude login (no API key).
  - **Managed via the `devcontainer` CLI** (`devcontainer up/exec`) + VS Code, modeled on the user's
    `~/dev/hello-dev-container` conventions — NOT plain `docker run` (the old `run.sh` was removed).
  - **Option A layout:** `.devcontainer/` at the **repo root** (whole repo = workspace, mounted at
    `/workspaces/expt-skill-wotkflow-agent`). `test-toy-greet-plugin/` is the in-container **scratch
    project** where we install + run `/greet`. Plugin source stays in `toy-greet-plugin/`.
  - Base: `mcr.microsoft.com/devcontainers/python:3.12` + uv; Node.js + Claude Code via devcontainer
    **features** (node feature first, then `anthropics/devcontainer-features/claude-code`).
  - Container `~/.claude` persisted via named volume `expt-skill-workflow-claude`; `postCreateCommand`
    chowns it to `vscode`. `DISABLE_AUTOUPDATER=1`.
  - Reused to test the final product (which commits code).
  - Authorship identity everywhere: **Soumendra Daas / soumendra.daas@gmail.com** (never Skye).

## Artifacts built so far
- `toy-greet-plugin/.claude-plugin/plugin.json` — toy plugin manifest
- `toy-greet-plugin/commands/greet.md` — `/greet` command implementing a 2-gate workflow
- `.devcontainer/Dockerfile` — mcr python:3.12 base + uv (Option A, repo root)
- `.devcontainer/devcontainer.json` — features (node + claude-code), volume, postCreate chown
- `DEVCONTAINER.md` — devcontainer lifecycle (CLI) + VS Code ⇧⌘P command reference
- `test-toy-greet-plugin/README.md` — the in-container scratch project (install + run `/greet`)
- `.claude-plugin/marketplace.json` — local marketplace `toy-local-marketplace` listing `toy-greet`
  (verified valid by claude-code-guide; installed + ran successfully in the container)
- `implement-feature-plugin/` — the REAL product scaffold (Chunk 10):
  - `.claude-plugin/plugin.json` — manifest
  - `commands/implement-feature.md` — thin conductor entry (loads the skill)
  - `skills/implement-feature/SKILL.md` — conductor score (Gate 0 full incl. preflight + model plan;
    Gates 1–10 stubbed, fleshed in Chunks 11–18)
  - `skills/implement-feature/references/quality-standards.md` — Definition of Done (toolchain,
    green-def, coverage/mutation gates, concurrency policy)
  - `skills/implement-feature/references/requirements-template.md` — Gate 1 outbox structure
    (summary, functional ACs, non-functional ACs, constraints, boundary inventory, out-of-scope)
  - `skills/implement-feature/references/design-interface-template.md` — Gate 2 public contract (shared
    with the algorithm-blind test-writer)
  - `skills/implement-feature/references/design-internal-template.md` — Gate 2 algorithm + alternatives
    (ADR), withheld from the test-writer
  - `skills/implement-feature/references/test-plan-template.md` — Gate 2 test inventory + coverage &
    mutation thresholds + concurrency plan
  - `toolchain/requirements-dev.txt` — pinned dev tools (installed by `.devcontainer` postCreate)
  - `agents/{test-writer,test-reviewer,implementer,verifier,code-reviewer}.md` — model-pinned isolated
    gates (read-only critics via `disallowedTools`; test-writer blind to `design-internal.md`)
  - `hooks/hooks.json` + `hooks/scripts/guard.py` — PreToolUse guard: audit log + secrets/.env deny
    (all agents) + `design-internal.md` deny (test-writer only). Validated in the container.
- `design/isolation-experiments.md` — the isolation investigation (facts, experiments, final posture)
- `LAUNCHING-SUBAGENTS.md` (repo root) — general guidelines: problems + mechanisms for launching/
  isolating subagents (model, effort, tools, read-confinement, secrets, per-agent access, audit)
