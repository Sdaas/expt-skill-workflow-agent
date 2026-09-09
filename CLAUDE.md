# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## What this repo is

A **hands-on tutorial project** for learning to build a Claude Code **plugin** that drives a full
human-in-the-loop workflow using **skills + subagents + workflow patterns — no orchestration code**.
It is a **learning exercise, not production code.** The end product is the `implement-feature-plugin`:
an `/implement-feature` slash command that runs an interview → spec → test-first → review → commit
pipeline.

Two plugins live here: `toy-greet-plugin/` (a minimal 2-gate learning scaffold) and
`implement-feature-plugin/` (the real product). Both are published through the local
`.claude-plugin/marketplace.json`.

## Working conventions (read before editing)

This project runs as a **paced tutorial**, and these standing rules from `PLAN.md` govern how to work
here — they override normal defaults:

1. **Pacing:** teach one chunk (~200–250 words) → comprehension check → advance **only** when the user
   says "next" (or similar). Do not run ahead.
2. **Docs update only on advance:** update `RESUME.md`, `TUTORIAL.md`, `PATTERNS.md` **only** when the
   user says "next", not mid-chunk.
3. **Q&A capture:** mid-chunk questions get condensed into `TUTORIAL.md` at the next advance.
4. **Commit per chunk:** on each "next", after recording docs, commit that chunk's changes — one commit
   per chunk. Never accumulate multiple chunks of uncommitted work.
5. Temp/scratch files go to `/tmp/` or end in `.tmp`, and are deleted when done.
6. Authorship for commits and generated code: **Soumendra Daas / soumendra.daas@gmail.com**.

**Start a new session by reading `RESUME.md`** — it is the live progress tracker and resume pointer.

## Key documents (the source of truth lives in Markdown, not code)

| File | Role |
|---|---|
| `RESUME.md` | Live progress + resume pointer. **Start here.** |
| `PLAN.md` | The 21-chunk tutorial plan, the 11-gate product design, and the change-of-direction log. |
| `TUTORIAL.md` | Accumulating concept reference + captured Q&A. |
| `PATTERNS.md` | Running design-patterns / anti-patterns / traps checklist (referenced as P1, P15, …). |
| `LAUNCHING-SUBAGENTS.md` | Empirical report on subagent isolation mechanisms (what is proven vs best-effort). |
| `design/isolation-experiments.md` | The experiments backing the isolation claims. |
| `DEVCONTAINER.md` | Dev-container lifecycle (CLI + VS Code palette). |

## Architecture: the `/implement-feature` conductor + isolated gates

The whole product is expressed **declaratively** — a skill (`SKILL.md`) is the "score", agent-definition
files pin per-gate models, and a hook enforces isolation. There is no hand-written orchestration driver.

- **Conductor [C]** — the interactive session running the skill
  (`implement-feature-plugin/skills/implement-feature/SKILL.md`). It holds the through-line, talks to the
  human, and walks 11 gates (0–10) in order.
- **Isolated subagents [I]** — bias-sensitive gates run as **separate agents** with fresh context, a
  **pinned model/effort**, and a **curated file inbox**. They are spawned via the Agent tool using the
  **plugin-namespaced** `subagent_type`, e.g. `implement-feature:test-writer` (never the bare name).
  Definitions live in `implement-feature-plugin/agents/*.md` — model/effort/tools are pinned there
  (`effort` can only be set via agent-def frontmatter, not inline).
- **The handoff contract:** every gate reads a curated inbox and writes a defined outbox **as files**
  under `<workdir>/handoff/` — a gate **never** sees a prior gate's raw transcript. The
  interface/internal **design split** keeps the test-writer algorithm-blind: it is handed
  `design-interface.md` but **never** `design-internal.md`.

The core invariants (also in `SKILL.md` → Rules): design & every review use a higher model/effort than
implementation; green unit tests are not "Done" (VERIFY drives the real code un-mocked); bound every
automated loop and surface to the human on no progress; **never commit before human approval (Gate 9)**.

### The guard hook (isolation is enforced, not just requested)

`implement-feature-plugin/hooks/hooks.json` registers a **PreToolUse** hook
(`hooks/scripts/guard.py`) that fires for the conductor **and every subagent** and keys on `agent_type`.
It does four jobs on every Read/Bash/Grep/Glob/Edit/Write:
1. **Audit** — appends a JSONL line per tool call (run-log path from `$IF_RUNLOG`, else
   `$CLAUDE_PROJECT_DIR/if-runlog.jsonl`, else `/tmp/if-runlog.jsonl`).
2. **Secrets guardrail** — denies reading `.env`/keys/credentials for any agent.
3. **Algorithm-blind** — denies the `test-writer` reading `design-internal.md`.
4. **Test-integrity** — denies the `implementer` editing/writing any test file.

A **plugin** hook (not a project-settings hook) was required for it to fire for subagents in headless.

### Quality standards / toolchain (single source of truth)

`implement-feature-plugin/skills/implement-feature/references/quality-standards.md` defines "green",
coverage/mutation thresholds, and concurrency policy. The pinned toolchain is
`implement-feature-plugin/toolchain/requirements-dev.txt` (ruff, mypy, pytest, pytest-cov, mutmut,
hypothesis, pytest-asyncio). Gate 0 preflight hard-fails if any tool is missing.

## Running / testing the plugins (dev container only)

**The plugin is never installed into the Mac's global `~/.claude`.** It is installed and run inside a
**dev container** with its own isolated `~/.claude` (login persisted in the named volume
`expt-skill-workflow-claude`). The container also has the pinned Python toolchain (installed by
`postCreateCommand`), which the real product depends on. Full lifecycle is in `DEVCONTAINER.md`.

```bash
# On the Mac, from the repo root (Docker Desktop must be running):
devcontainer up --workspace-folder .                    # build if needed + start (idempotent)
devcontainer up --workspace-folder . --build            # rebuild after editing .devcontainer/*
devcontainer exec --workspace-folder . bash             # shell inside
devcontainer exec --workspace-folder . claude           # jump into Claude Code inside
```

Inside the container, install from the local marketplace and run:
```
/plugin marketplace add <repo path>      # then: claude plugin install <plugin>
/toy-greet:greet                          # toy 2-gate workflow
/implement-feature                        # the real product
```
`test-toy-greet-plugin/` is the in-container scratch project where the toy is installed and run.

## When editing the product

- The **behavior lives in Markdown** (`SKILL.md`, `agents/*.md`, `references/*`, `hooks.json`). Editing
  the workflow means editing these files, not writing code. The only real code is `guard.py` (a hook)
  and the future deterministic transcript analyzer (measurement, not orchestration — both allowed).
- Changing a gate's model/effort/tools → edit the matching `agents/*.md` frontmatter.
- Changing what an agent may read/write → update both the agent's prose inbox **and** `guard.py`
  (defense-in-depth: role instruction + hook enforcement).
- Reference `PATTERNS.md` entries (P#) when they apply; add new traps there.
