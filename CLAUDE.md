# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

> ⚠️ **This repo is mid-refactor.** It is being converted from a paced learning tutorial into a
> **genuinely usable** `implement-feature` Claude Code plugin. The old paced-tutorial conventions
> (teach one ~250-word chunk → comprehension check → wait for "next" → commit-per-chunk) are
> **RETIRED — do not follow them.** Work now proceeds as **plan → approve → phased execution**.

## Resuming a session (read this first)
1. `git checkout refactor/shippable-plugin` — all refactor work lives on this branch.
2. Read **`REFACTOR-PLAN.md`** — the live source of truth: goal, issue triage, phases, done-gate
   (§0 CURRENT STATE + §5 progress log tell you exactly where we are).
3. **`RESUME.md`** holds the paste-ready resume prompt + environment steps — current and
   maintained (it and `REFACTOR-PLAN.md` are transient, deleted only at merge in Phase 5).
4. `PLAN.md` is **stale / being deleted** by this refactor; do not treat it as current.

## What this repo is (target end-state)
A **one repo** that ships a genuinely-usable `implement-feature` plugin, with a top-level `README.md`
routing **three audiences**:
- **User Guide** (`docs/user-guide.md`) — install from GitHub, Python-only setup + toolchain
  prerequisite, how to run, FAQ. For a real user on their **own machine / own repo**.
- **Developer Guide** (`docs/developer-guide.md`) — architecture, ADRs, design principles, the guard
  hook, the analyzer, and the testing / dry-run methodology. For someone improving the plugin.
- **Tutorial** (`docs/tutorial.md`) — concepts (plugin vs command vs skill vs workflow) + subagent
  isolation, with `toy-greet-plugin/` as the runnable example.

Two plugins live here: `toy-greet-plugin/` (a minimal 2-gate example, kept for the Tutorial) and
`implement-feature-plugin/` (**the product**). Both are published through `.claude-plugin/marketplace.json`.

## Working conventions
- **Process:** plan → approve → phased execution on `refactor/shippable-plugin`. Commit per **logical
  unit** (not per chunk). Keep git history.
- **Bar:** *genuinely usable* — a stranger can install from GitHub and run it against their own Python
  repo. "Done" = a **green end-to-end dry run in the dev container** (see `REFACTOR-PLAN.md`), not
  "docs exist."
- Temp/scratch files go to `/tmp/` or end in `.tmp`, deleted when done.
- Authorship for commits and generated code: **Soumendra Daas / soumendra.daas@gmail.com**.

## Architecture: the `/implement-feature` conductor + isolated gates
The whole product is expressed **declaratively** — a skill (`SKILL.md`) is the "score", agent-definition
files pin per-gate models, and a hook enforces isolation. There is no hand-written orchestration driver.

- **Conductor [C]** — the interactive session running the skill
  (`implement-feature-plugin/skills/implement-feature/SKILL.md`). It holds the through-line, talks to the
  human, and walks 12 gates (0–11) in order.
- **Isolated subagents [I]** — bias-sensitive gates run as **separate agents** with fresh context, a
  **pinned model/effort**, and a **curated file inbox**. They are spawned via the Agent tool using the
  **plugin-namespaced** `subagent_type`, e.g. `implement-feature:test-writer` (never the bare name).
  Definitions live in `implement-feature-plugin/agents/*.md` — model/effort/tools are pinned there
  (`effort` can only be set via agent-def frontmatter, not inline).
- **The handoff contract:** every gate reads a curated inbox and writes a defined outbox **as files** —
  a gate **never** sees a prior gate's raw transcript. The interface/internal **design split** keeps the
  test-writer algorithm-blind: it is handed `design-interface.md` but **never** `design-internal.md`.
  (Note: the workdir/handoff layout is being redesigned — issue #10 — see `REFACTOR-PLAN.md`.)

Core invariants (also in `SKILL.md` → Rules): design & every review use a higher model/effort than
implementation; green unit tests are not "Done" (VERIFY drives the real code un-mocked); bound every
automated loop and surface to the human on no progress; **never commit before human approval**.

### The guard hook (isolation is enforced, not just requested)
`implement-feature-plugin/hooks/hooks.json` registers a **PreToolUse** hook (`hooks/scripts/guard.py`)
that fires for the conductor **and every subagent** and keys on `agent_type`. On every
Read/Bash/Grep/Glob/Edit/Write it: (1) **audits** — appends a JSONL line per tool call; (2) **secrets
guardrail** — denies reading `.env`/keys/credentials for any agent; (3) **algorithm-blind** — denies the
`test-writer` reading `design-internal.md`; (4) **test-integrity** — denies the `implementer`
editing/writing any test file. A **plugin** hook (not a project-settings hook) was required for it to
fire for subagents in headless.

### Quality standards / toolchain (single source of truth)
`implement-feature-plugin/skills/implement-feature/references/quality-standards.md` defines "green",
coverage/mutation thresholds, and concurrency policy. The pinned toolchain is
`implement-feature-plugin/toolchain/requirements-dev.txt` (ruff, mypy, pytest, pytest-cov, mutmut,
hypothesis, pytest-asyncio). Gate 0 preflight hard-fails if any tool is missing. **A real user must
install this toolchain into their own environment** (v1: documented manual install; auto-install is a
v1.1 backlog item).

## Running / testing the plugin (dev container = our test harness)
**The plugin is never installed into the Mac's global `~/.claude`.** For *our* testing it is installed and
run inside a **dev container** with its own isolated `~/.claude` (login persisted in the named volume
`expt-skill-workflow-claude`), which also has the pinned Python toolchain. Full lifecycle in
`DEVCONTAINER.md`. (A *real end user* installs on their own machine — that path is the User Guide's job.)

```bash
# On the Mac, from the repo root (Docker Desktop must be running):
devcontainer up --workspace-folder .          # build if needed + start (idempotent)
devcontainer exec --workspace-folder . bash   # shell inside
devcontainer exec --workspace-folder . claude # jump into Claude Code inside
```

## When editing the product
- The **behavior lives in Markdown** (`SKILL.md`, `agents/*.md`, `references/*`, `hooks.json`). Editing
  the workflow means editing these files, not writing code. The only real code is `guard.py` (the hook)
  and `analyzer/` (deterministic measurement, not orchestration — both allowed).
- Changing a gate's model/effort/tools → edit the matching `agents/*.md` frontmatter.
- Changing what an agent may read/write → update both the agent's prose inbox **and** `guard.py`
  (defense-in-depth: role instruction + hook enforcement).
