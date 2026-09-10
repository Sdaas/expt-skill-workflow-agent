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
- **Current phase:** Part D — Build the real product (dry run complete; wrap next)
- **Last completed chunk:** Chunk 21 ✅ (2026-09-10, **end-to-end dry run**) — ran the real
  `/implement-feature` on `parse_duration` inside the container through all 11 gates + guard hook, then
  ran the analyzer on the real logs. **Validated the core design:** model pinning is real (2 subagents
  on `claude-opus-5` = the review gates, 4 on `claude-sonnet-5`), isolation held (test-writer
  algorithm-blind, implementer never touched tests, 5 distinct subagents), pipeline committed. The run
  was a **bug-finding machine** → filed **13 GitHub issues (#5–#17)**, incl. two analyzer bugs
  (#15 blind to `subagents/*.jsonl`; #16 secret false-positive on Bash strings) and the "`disallowedTools`
  is not a sandbox when Bash is granted" finding (#12). Only code change committed: the **mutmut preflight
  fix** (metadata check, not `mutmut --version`, which false-fails in a source-less dir). Everything else
  is captured as issues, not implemented. Added **P44–P51**. **Next: PLAN item 21 (wrap: package +
  concept recap).**
- **Open issues from the dry run (#5–#17):** #5 read-tax, #6 UG, #7 DG, #8 branch-assessment,
  #9 `/resume-feature`, #10 workdir-redesign(+log-wart), #11 review-real-artifact, #12 test-reviewer
  confinement, #13 mutation-anchor, #14 post-run-analysis-command, #15 analyzer-subagents, #16
  secret-false-positive, #17 numbered-handoff-files. **These are the backlog for a future build phase.**
- **Superseded — Chunk 20 ✅ (2026-09-09, build):** built the **observability analyzer**
  `implement-feature-plugin/analyzer/` (test-first, ruff+mypy clean, 16 tests). Two independent readers:
  `runlog.py` (load-bearing; per-agent activity + 4 isolation verdicts) and `transcript.py` (best-effort
  satellite; per-model tokens, schema self-check, soft `TranscriptAbsent` / loud `TranscriptFormatError`);
  `report.py` pure rendering; `analyze_run.py` CLI with the transcript quarantine; `_util.py` tolerant
  UTC parsing. Also fixed `guard.py` to log UTC/tz-aware (shared clock for correlation) and fixed the
  **devcontainer postCreate** (sudo-preserve-PATH install + metadata mutmut check → `outcome=success`).
  Live-demoed on THIS session's transcript (correlation by time-window picked the right `.jsonl`).
  Patterns added: **P41** fail-loud, **P42** stable-core+quarantined-satellite, **P43** correlate-by-value.
- **Chunk numbering note:** PLAN item 19 (promote the analyzer) was delivered across **session chunks 19
  (concept) + 20 (build)**, so session-chunk numbers now run **one ahead** of PLAN item numbers.
- **Current chunk (NEXT):** session chunk 22 = PLAN item 21 (**wrap**: package + concept recap). Before
  that, a queued discussion: **the testing methodology itself** — a dry run should start from a
  **bootstrapped python git repo** (pyproject/toml + `src/` + `tests/`), not a clean folder, because the
  skill assumes (a) a git repo, (b) python, (c) identified src/tests dirs.

## How to run a dry run (reference — chunk 21 done)
The scratch project is **`~/test-implement-feature`** in the container (own git repo, ambient identity
`Soumendra Daas <soumendra.daas@gmail.com>`). The `implement-feature@toy-local-marketplace` plugin is
installed there. To run again:
1. `devcontainer up --workspace-folder .` (idempotent). Verify `claude plugin list` shows
   `implement-feature@toy-local-marketplace`; reinstall if not (`claude plugin marketplace update
   toy-local-marketplace && claude plugin uninstall implement-feature && claude plugin install
   implement-feature@toy-local-marketplace`). **Reinstall after ANY edit to `SKILL.md`/`guard.py`/
   `analyzer/`** — the run uses the *cached* copy, and a running `claude` session must be restarted to
   pick up a reinstall.
2. **In a terminal (needs a TTY — not the agent's Bash tool):**
   `devcontainer exec --workspace-folder /Users/sdaas/dev/expt-skill-workflow-agent bash`, then
   `cd ~/test-implement-feature && claude`, then `/implement-feature`.
3. Feature brief for INTERVIEW: `parse_duration(s)->int` seconds; ordered h/m/s each ≤once; ValueError on
   empty/no-units/unknown-unit/wrong-order/dup/negative/non-numeric; pure fn, no concurrency (N/A).
4. Gates: 1 INTERVIEW → 2 DESIGN (STOP) → 3–7 auto (isolated subagents) → 8 REVIEW-GUIDE →
   9 HUMAN REVIEW (STOP) → 10 COMMIT. **Workaround until #11:** at DESIGN, ask the conductor to paste the
   full design inline before approving (it writes files only after approval today).
5. **Analyze the run** (the analyzer's transcript reader currently misses subagents — see #15):
   `devcontainer exec --workspace-folder /Users/sdaas/dev/expt-skill-workflow-agent bash -lc 'cd /workspaces/expt-skill-workflow-agent/implement-feature-plugin && python -m analyzer.analyze_run --runlog ~/test-implement-feature/if-runlog.jsonl --projects-dir ~/.claude/projects --slug=-home-vscode-test-implement-feature'`
   (note `--slug=` equals-form: a leading-dash slug is otherwise parsed as a flag). Subagent transcripts
   are under `~/.claude/projects/<slug>/<uuid>/subagents/*.jsonl` (opus vs sonnet per gate).

## Resuming the container next session (quick ref)
> NOTE (2026-09-07 pause): the container **and image were deleted** at session end, but the login
> **volume `expt-skill-workflow-claude` was kept**. So `devcontainer up` will **rebuild the image**
> (slower first time; postCreate reinstalls the toolchain) — login should still persist via the volume.
> Also **reinstall the `implement-feature` plugin** on resume so the cached copy picks up the Chunk-15
> guard-hook update (4th job: implementer can't edit tests): `claude plugin marketplace update
> toy-local-marketplace && claude plugin uninstall implement-feature && claude plugin install
> implement-feature@toy-local-marketplace`.
1. `cd /Users/sdaas/dev/expt-skill-wotkflow-agent`
2. `devcontainer up --workspace-folder .`  (rebuilds the image this time; recreates the container)
3. `devcontainer exec --workspace-folder . claude`  (login persists via the volume; usually no re-login)
4. The `toy-local-marketplace` + `toy-greet` install persist in the `~/.claude` volume; if
   `/toy-greet:greet` isn't present, re-run `claude plugin install toy-greet@toy-local-marketplace`
   then `/reload-plugins`. See `DEVCONTAINER.md` for full lifecycle.

## Progress log
- 2026-09-10 — **Chunk 21 ✅ (end-to-end dry run)**: ran real `/implement-feature` on `parse_duration`
  in the container through all 11 gates + guard, then analyzed the logs. Validated model pinning
  (opus-5 reviewers, sonnet-5 impl) + isolation + a committed result. Filed **13 issues (#5–#17)** —
  the improvement backlog. Committed the **mutmut preflight fix** (metadata check) + these doc updates.
  Added **P44–P51**. Key findings: `disallowedTools`≠sandbox with Bash (#12); analyzer blind to
  `subagents/*.jsonl` (#15); secret false-positive on Bash strings (#16); approve-a-summary gap (#11);
  workdir==repo-root collision (#10). **Next: PLAN item 21 (wrap), after discussing the testing
  methodology (bootstrapped-python-repo starting point).**
- 2026-09-09 — **Chunk 20 ✅ (build)**: built `implement-feature-plugin/analyzer/` — two decoupled
  readers (`runlog.py` load-bearing + `transcript.py` best-effort satellite), `report.py`,
  `analyze_run.py` (transcript quarantine), `_util.py`, `README.md`, 16 tests (ruff+mypy clean in the
  container). Fixed `guard.py` → UTC/tz-aware run-log ts (shared clock). Fixed devcontainer postCreate
  (2 regressions: root-write install + mutmut liveness). Live-demoed on this session's transcript.
  Added P41/P42/P43. Committed (analyzer + guard) — devcontainer fix committed separately (0d658e8).
  **Next: end-to-end dry run in the sandbox (PLAN item 20).**
- 2026-09-09 — **Chunk 19 ✅ (concept)**: taught the observability analyzer (deterministic Python; reads
  `if-runlog.jsonl` + transcript; per-gate model/tokens/reads + isolation-compliance pass/fail). Added
  **P40** (measure-never-orchestrate: the one code exception alongside `guard.py`). Also cleared the
  Chunk 18 comprehension check. Discovered the devcontainer `postCreate` permission regression (see
  Status blocker). Committed. **Next: Chunk 20 = build the analyzer.**
- 2026-09-09 — **Chunk 17 design revision** (during a walk-through of Chunks 14–18, user-driven):
  fixed a real routing bug in Gate 7 CODE-REVIEW. Coverage/mutation failures were looping back to
  IMPLEMENT, but the implementer is barred from editing tests (guard job #4) → dead-end loop. Now
  every review finding is **TYPED** (`→IMPLEMENT` for code defects / `→TESTS` for weak-or-missing
  tests) and the conductor routes each to the right gate (`→TESTS` re-enters WRITE-TESTS +
  TEST-REVIEW). Kept **one gate / one review pass, two repair paths**. Also enriched the review
  rubric to the **six `claude-sdlc` quality dimensions** (added performance, reliability,
  observability). Edited `SKILL.md` Gate 7 + `agents/code-reviewer.md`; added P37/P38. Committed.
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
- 2026-09-07 — Chunk 18 ✅ (build): fleshed Gates 8–10 (REVIEW-GUIDE → HUMAN REVIEW → COMMIT). The
  11-gate conductor score is COMPLETE (no stubs). Added P36 (human gate owns the ship decision; cheap
  models for mechanical gates). Committed + pushed; container/image torn down (login volume kept).
- 2026-09-07 — Chunk 17 ✅ (build): fleshed Gate 7 CODE-REVIEW in `SKILL.md` — whole-diff Opus reviewer,
  judgement review + slow checks (pytest-cov coverage, mutmut mutation vs thresholds), flags tests/
  changes, bounded loop to IMPLEMENT. Added P35 (mutation retroactively grades test quality). Committed.
- 2026-09-07 — Chunk 16 ✅ (build): fleshed Gate 6 VERIFY in `SKILL.md` — fresh read-only verifier,
  drive real feature per-AC + un-mocked boundaries; outer loop back to IMPLEMENT on defect. Added P34
  (nested inner/outer loop). Committed.
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
  - `hooks/hooks.json` + `hooks/scripts/guard.py` — PreToolUse guard: audit log (now **UTC/tz-aware**
    ts, for analyzer correlation) + secrets/.env deny (all agents) + `design-internal.md` deny
    (test-writer only) + implementer-can't-write-tests. Validated in the container.
  - `analyzer/` — the **observability analyzer** (Chunk 20): `runlog.py` (load-bearing: per-agent
    activity + 4 isolation verdicts from `if-runlog.jsonl`), `transcript.py` (best-effort satellite:
    per-model tokens, schema self-check, `TranscriptAbsent`/`TranscriptFormatError`), `report.py` (pure
    Markdown), `analyze_run.py` (CLI + transcript quarantine), `_util.py`, `README.md`, `tests/` (16
    tests). Run: `python -m analyzer.analyze_run --runlog if-runlog.jsonl`. ruff+mypy clean.
  - `conftest.py` (plugin root) — puts the plugin dir on sys.path so `analyzer` imports under pytest.
- `design/isolation-experiments.md` — the isolation investigation (facts, experiments, final posture)
- `LAUNCHING-SUBAGENTS.md` (repo root) — general guidelines: problems + mechanisms for launching/
  isolating subagents (model, effort, tools, read-confinement, secrets, per-agent access, audit)
