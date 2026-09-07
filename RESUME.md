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

## Status
- **Current phase:** Part D — Build the real product
- **Last completed chunk:** Chunk 10 ✅ (2026-09-07) — scaffolded `implement-feature-plugin/`: thin
  command → `implement-feature` skill (conductor score, Gate 0 FULL incl. preflight + model plan,
  Gates 1–10 stubbed), 5 model-pinned agent-def files, a pinned **toolchain** + a **quality-standards**
  reference. Folded in the quality dimension the user flagged: ruff/mypy/pytest gate the IMPLEMENT
  inner loop; pytest-cov + mutmut gate CODE-REVIEW (split-by-speed); Gate 0 hard-fail preflight;
  concurrency = boundary-driven; tools pinned + installed in the dev container. Committed.
- **Next chunk to deliver:** Chunk 11 (Part D) — flesh the grilling-style **INTERVIEW** gate (Gate 1)
  → `requirements.md` with functional + non-functional ACs + constraints + boundary inventory.
- **Awaiting from user:** delivering Chunk 11 now (user said "next … then continue").

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
  - `toolchain/requirements-dev.txt` — pinned dev tools (installed by `.devcontainer` postCreate)
  - `agents/{test-writer,test-reviewer,implementer,verifier,code-reviewer}.md` — model-pinned isolated
    gates (read-only critics via `disallowedTools`; test-writer blind to `design-internal.md`)
